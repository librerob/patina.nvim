// Run in a disposable VS Code Extension Development Host under xvfb-run.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const modules = process.env.VERDELLE_NODE_MODULES;
const dependency = name => require(path.join(modules, name));

async function syntax(theme, palette, appRoot) {
  const textmate = dependency('vscode-textmate');
  const oniguruma = dependency('vscode-oniguruma');
  const wasm = fs.readFileSync(path.join(modules, 'vscode-oniguruma/release/onig.wasm'));
  await oniguruma.loadWASM(wasm.buffer.slice(wasm.byteOffset, wasm.byteOffset + wasm.byteLength));
  for (const [extension, language, example] of [
    ['lua', 'lua', 'library.lua'], ['python', 'python', 'index.py'],
    ['typescript-basics', 'typescript', 'client.ts'],
  ]) {
    const directory = path.join(appRoot, 'extensions', extension);
    const contribution = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8'));
    const grammarEntry = contribution.contributes.grammars.find(item => item.language === language);
    const registry = new textmate.Registry({
      theme: { settings: [{ settings: { foreground: palette.fg, background: palette.bg } }, ...theme.tokenColors] },
      onigLib: Promise.resolve({ createOnigScanner: patterns => new oniguruma.OnigScanner(patterns),
        createOnigString: value => new oniguruma.OnigString(value) }),
      loadGrammar: async scope => {
        const entry = contribution.contributes.grammars.find(item => item.scopeName === scope);
        if (!entry) return null;
        const filename = path.join(directory, entry.path);
        return textmate.parseRawGrammar(fs.readFileSync(filename, 'utf8'), filename);
      },
    });
    const grammar = await registry.loadGrammar(grammarEntry.scopeName);
    assert(grammar, `Missing ${language} grammar`);
    let stack = textmate.INITIAL;
    const seen = new Set();
    const allowed = new Set(Object.values(palette));
    const fixture = language === 'python' ? '\n# Comment fixture' : language === 'typescript' ? '\nconst label = "Verdelle";' : '';
    for (const line of (fs.readFileSync(path.join(root, 'tests/fixtures', example), 'utf8') + fixture).split(/\r?\n/)) {
      const result = grammar.tokenizeLine2(line, stack);
      stack = result.ruleStack;
      const colors = registry.getColorMap();
      for (let index = 1; index < result.tokens.length; index += 2) {
        const color = colors[(result.tokens[index] >>> 15) & 0x1ff].toUpperCase();
        assert(allowed.has(color), `${language}: off-palette token ${color}`);
        seen.add(color);
      }
    }
    for (const role of ['keyword', 'string', 'func', 'comment']) {
      assert(seen.has(palette[role]), `${language} did not resolve ${role}`);
    }
    registry.dispose();
  }
}

async function webviewColors(vscode, keys, expectedBackground) {
  const panel = vscode.window.createWebviewPanel('verdelle-test', 'Verdelle colors', vscode.ViewColumn.One,
    { enableScripts: true });
  try {
    return await new Promise((resolve, reject) => {
      let lastColors;
      const timer = setTimeout(() => reject(new Error(`Theme CSS probe timed out: ${JSON.stringify(lastColors)}`)), 15000);
      const subscription = panel.webview.onDidReceiveMessage(colors => {
        lastColors = colors;
        // Updating settings crosses the renderer/extension-host boundary. The
        // theme kind alone cannot distinguish Verdelle from another dark theme.
        const target = expectedBackground.slice(1).match(/../g).map(value => parseInt(value, 16));
        const background = colors['editor.background'];
        if (background.toUpperCase() !== expectedBackground &&
            background !== `rgb(${target.join(', ')})`) return;
        clearTimeout(timer);
        subscription.dispose();
        resolve(colors);
      });
      panel.webview.html = `<!doctype html><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-verdelle-test'">
        <script nonce="verdelle-test">
        const vscode = acquireVsCodeApi();
        function sample() {
          const style = getComputedStyle(document.documentElement);
          vscode.postMessage(Object.fromEntries(${JSON.stringify(keys)}.map(key =>
            [key, style.getPropertyValue('--vscode-' + key.replaceAll('.', '-')).trim()])));
        }
        sample();
        setInterval(sample, 50);
        </script>`;
    });
  } finally {
    panel.dispose();
  }
}

exports.run = async function () {
  const vscode = require('vscode');
  assert(vscode.extensions.getExtension('librerob.verdelle-theme'), 'Theme extension did not register');
  await vscode.workspace.getConfiguration('window').update('autoDetectColorScheme', false, vscode.ConfigurationTarget.Global);
  await vscode.workspace.getConfiguration('window').update('autoDetectHighContrast', false, vscode.ConfigurationTarget.Global);
  for (const variant of ['dark', 'light', 'dark']) {
    const suffix = variant === 'light' ? '-light' : '';
    const data = JSON.parse(fs.readFileSync(path.join(root, `palette/${variant}.json`), 'utf8'));
    const theme = JSON.parse(fs.readFileSync(path.join(root, `ports/vscode/themes/verdelle${suffix}-color-theme.json`), 'utf8'));
    await vscode.workspace.getConfiguration('workbench').update('colorTheme', data.name, vscode.ConfigurationTarget.Global);
    const expectedKind = variant === 'dark' ? vscode.ColorThemeKind.Dark : vscode.ColorThemeKind.Light;
    console.log(`Applying ${data.name}; setting=${vscode.workspace.getConfiguration('workbench').get('colorTheme')}; kind=${vscode.window.activeColorTheme.kind}`);
    const pairs = { 'editor.background': 'bg', 'editor.foreground': 'fg', 'sideBar.background': 'panel',
      'editorInlayHint.foreground': 'comment', 'editorInlayHint.typeForeground': 'comment',
      'editorInlayHint.parameterForeground': 'comment', 'editorCodeLens.foreground': 'comment',
      'editorSuggestWidget.background': 'float', 'editorSuggestWidget.foreground': 'fg',
      'editor.selectionForeground': 'selection_fg', 'editor.selectionBackground': 'selection',
      'editorSuggestWidget.selectedBackground': 'menu_selection',
      'list.activeSelectionBackground': 'menu_selection', 'list.activeSelectionForeground': 'fg' };
    const actual = await webviewColors(vscode, Object.keys(pairs), data.colors.bg);
    assert.equal(vscode.window.activeColorTheme.kind, expectedKind, 'Wrong active theme variant after UI update');
    const rgb = color => color.match(/^#[0-9a-f]{6}$/i) ? color.toUpperCase() :
      '#' + color.match(/[\d.]+/g).slice(0, 3).map(channel => Number(channel).toString(16).padStart(2, '0')).join('').toUpperCase();
    for (const [key, role] of Object.entries(pairs)) {
      assert(actual[key], `Unregistered VS Code color ${key}`);
      assert.equal(rgb(actual[key]), data.colors[role], `${variant} ${key} default color leaked`);
    }
    await syntax(theme, data.colors, vscode.env.appRoot);
    const document = await vscode.workspace.openTextDocument(path.join(root, 'tests/fixtures/client.ts'));
    const editor = await vscode.window.showTextDocument(document);
    editor.selection = new vscode.Selection(0, 0, 0, 12);
    await vscode.commands.executeCommand('editor.action.selectHighlights');
    console.log(`VS Code ${variant}: active theme, resolved UI colors and Lua/Python/TypeScript grammars passed`);
  }
};

if (require.main === module) {
  // Older development hosts pin the first theme from the development extension
  // in memory. Install Verdelle normally and use an empty test-host extension so
  // variant switching follows the same path as a user's installed theme.
  const extensions = path.join(process.env.RUNNER_TEMP, 'verdelle-installed-extensions');
  const host = path.join(process.env.RUNNER_TEMP, 'verdelle-vscode-test-host');
  fs.mkdirSync(extensions, { recursive: true });
  fs.mkdirSync(host, { recursive: true });
  fs.cpSync(path.join(root, 'ports/vscode'), path.join(extensions, 'librerob.verdelle-theme'), { recursive: true });
  fs.writeFileSync(path.join(host, 'package.json'), JSON.stringify({ name: 'verdelle-test-host',
    publisher: 'verdelle-tests', version: '0.0.0', engines: { vscode: '^1.85.0' } }));
  dependency('@vscode/test-electron').runTests({
    version: process.env.VERDELLE_VSCODE_VERSION || 'stable',
    cachePath: path.join(process.env.RUNNER_TEMP, 'verdelle-vscode'),
    extensionDevelopmentPath: host, extensionTestsPath: __filename,
    launchArgs: ['--disable-gpu', '--skip-welcome', '--skip-release-notes', '--extensions-dir', extensions],
    extensionTestsEnv: { VERDELLE_NODE_MODULES: modules },
  }).catch(error => { console.error(error); process.exitCode = 1; });
}
