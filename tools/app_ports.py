"""Generate Verdelle ports. Adapted from librerob/morello (MIT)."""
import json
import plistlib


def outputs(palettes, generated):
    result = {}
    def write(path, text):
        result[path] = text.rstrip() + '\n'


    class Symbol(str):
        """An unquoted Lisp symbol inside a data expression."""


    def lisp(value):
        if value is True:
            return 't'
        if value is False:
            return 'nil'
        if isinstance(value, Symbol):
            return str(value)
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, dict):
            return '(' + ' '.join(f':{key} {lisp(item)}' for key, item in value.items()) + ')'
        return str(value)


    def emacs_faces(p, ansi):
        faces = {
            'default': {'foreground': p['fg'], 'background': p['bg']},
            'cursor': {'background': p['cursor']},
            'fringe': {'foreground': p['subdued'], 'background': p['bg']},
            'region': {'foreground': p['selection_fg'], 'background': p['selection'], 'extend': True},
            'secondary-selection': {'foreground': p['selection_fg'], 'background': p['selection'], 'extend': True},
            'hl-line': {'background': p['line'], 'extend': True},
            'highlight': {'foreground': p['selection_fg'], 'background': p['selection']},
            'line-number': {'foreground': p['subdued'], 'background': p['bg']},
            'line-number-current-line': {'foreground': p['focus'], 'background': p['line'], 'weight': Symbol('bold')},
            'vertical-border': {'foreground': p['border']},
            'window-divider': {'foreground': p['border']},
            'window-divider-first-pixel': {'foreground': p['border']},
            'window-divider-last-pixel': {'foreground': p['border']},
            'fill-column-indicator': {'foreground': p['border']},
            'shadow': {'foreground': p['comment']},
            'minibuffer-prompt': {'foreground': p['func'], 'weight': Symbol('bold')},
            'link': {'foreground': p['type'], 'underline': True},
            'link-visited': {'foreground': p['constant'], 'underline': True},
            'error': {'foreground': p['error'], 'weight': Symbol('bold')},
            'warning': {'foreground': p['warning']},
            'success': {'foreground': p['focus']},
            'mode-line': {'foreground': p['fg'], 'background': p['panel'], 'box': False},
            'mode-line-active': {'foreground': p['fg'], 'background': p['panel'], 'box': False},
            'mode-line-inactive': {'foreground': p['muted'], 'background': p['line'], 'box': False},
            'mode-line-buffer-id': {'foreground': p['func'], 'weight': Symbol('bold')},
            'header-line': {'foreground': p['muted'], 'background': p['panel'], 'box': False},
            'tooltip': {'foreground': p['fg'], 'background': p['float']},
            'isearch': {'foreground': p['search_current_fg'], 'background': p['search_current_bg']},
            'lazy-highlight': {'foreground': p['search_fg'], 'background': p['search_bg']},
            'match': {'foreground': p['search_fg'], 'background': p['search_bg']},
            'show-paren-match': {'foreground': p['cursor'], 'weight': Symbol('bold'), 'underline': True},
            'show-paren-mismatch': {'foreground': p['error'], 'weight': Symbol('bold')},
            'trailing-whitespace': {'background': p['error']},
            'whitespace-space': {'foreground': p['subdued']},
            'whitespace-tab': {'foreground': p['subdued']},
            'font-lock-comment-face': {'foreground': p['comment'], 'slant': Symbol('normal')},
            'font-lock-comment-delimiter-face': {'foreground': p['comment'], 'slant': Symbol('normal')},
            'font-lock-doc-face': {'foreground': p['comment'], 'slant': Symbol('normal')},
            'font-lock-doc-markup-face': {'foreground': p['comment']},
            'font-lock-keyword-face': {'foreground': p['keyword']},
            'font-lock-preprocessor-face': {'foreground': p['keyword']},
            'font-lock-builtin-face': {'foreground': p['type']},
            'font-lock-string-face': {'foreground': p['string']},
            'font-lock-function-name-face': {'foreground': p['func']},
            'font-lock-function-call-face': {'foreground': p['func'], 'slant': Symbol('normal')},
            'font-lock-variable-name-face': {'foreground': p['variable']},
            'font-lock-variable-use-face': {'foreground': p['variable']},
            'font-lock-property-name-face': {'foreground': p['variable']},
            'font-lock-property-use-face': {'foreground': p['variable']},
            'font-lock-constant-face': {'foreground': p['constant']},
            'font-lock-number-face': {'foreground': p['constant']},
            'font-lock-type-face': {'foreground': p['type']},
            'font-lock-operator-face': {'foreground': p['operator']},
            'font-lock-negation-char-face': {'foreground': p['operator']},
            'font-lock-punctuation-face': {'foreground': p['punctuation']},
            'font-lock-bracket-face': {'foreground': p['punctuation']},
            'font-lock-delimiter-face': {'foreground': p['punctuation']},
            'font-lock-warning-face': {'foreground': p['warning']},
            'font-lock-escape-face': {'foreground': p['constant']},
            'completions-common-part': {'foreground': p['func'], 'weight': Symbol('bold')},
            'completions-annotations': {'foreground': p['comment']},
            'completions-highlight': {'foreground': p['fg'], 'background': p['menu_selection']},
            'vertico-current': {'foreground': p['fg'], 'background': p['menu_selection'], 'extend': True},
            'corfu-default': {'foreground': p['fg'], 'background': p['float']},
            'corfu-current': {'foreground': p['fg'], 'background': p['menu_selection']},
            'corfu-border': {'background': p['border']},
            'company-tooltip': {'foreground': p['fg'], 'background': p['float']},
            'company-tooltip-selection': {'foreground': p['fg'], 'background': p['menu_selection']},
            'company-tooltip-annotation': {'foreground': p['comment']},
            'company-tooltip-common': {'foreground': p['func'], 'weight': Symbol('bold')},
            'diff-added': {'foreground': p['fg'], 'background': p['diff_add'], 'extend': True},
            'diff-removed': {'foreground': p['error'], 'background': p['diff_delete'], 'extend': True},
            'diff-changed': {'foreground': p['fg'], 'background': p['diff_change'], 'extend': True},
            'diff-refine-added': {'foreground': p['fg'], 'background': p['diff_text']},
            'diff-refine-removed': {'foreground': p['fg'], 'background': p['diff_text']},
            'diff-context': {'foreground': p['muted']},
            'diff-header': {'foreground': p['type'], 'background': p['line']},
            'diff-file-header': {'foreground': p['func'], 'background': p['panel'], 'weight': Symbol('bold')},
            'magit-section-heading': {'foreground': p['func'], 'weight': Symbol('bold')},
            'magit-diff-added': {'foreground': p['fg'], 'background': p['diff_add'], 'extend': True},
            'magit-diff-removed': {'foreground': p['error'], 'background': p['diff_delete'], 'extend': True},
            'magit-diff-added-highlight': {'foreground': p['fg'], 'background': p['diff_add'], 'extend': True},
            'magit-diff-removed-highlight': {'foreground': p['error'], 'background': p['diff_delete'], 'extend': True},
            'magit-diff-context': {'foreground': p['muted']},
            'magit-diff-context-highlight': {'foreground': p['fg'], 'background': p['line'], 'extend': True},
            'magit-diff-hunk-heading': {'foreground': p['type'], 'background': p['line']},
            'magit-diff-hunk-heading-highlight': {'foreground': p['selection_fg'], 'background': p['selection']},
            'magit-branch-local': {'foreground': p['func']},
            'magit-branch-remote': {'foreground': p['type']},
            'org-document-title': {'foreground': p['func'], 'weight': Symbol('bold')},
            'org-link': {'foreground': p['type'], 'underline': True},
            'org-code': {'foreground': p['string']},
            'org-verbatim': {'foreground': p['string']},
            'org-block': {'foreground': p['fg'], 'background': p['panel'], 'extend': True},
            'org-block-begin-line': {'foreground': p['comment'], 'background': p['panel'], 'extend': True},
            'org-block-end-line': {'foreground': p['comment'], 'background': p['panel'], 'extend': True},
            'org-todo': {'foreground': p['warning'], 'weight': Symbol('bold')},
            'org-done': {'foreground': p['focus']},
            'org-date': {'foreground': p['constant']},
            'org-meta-line': {'foreground': p['comment']},
            'doom-modeline-bar': {'background': p['func']},
            'doom-modeline-buffer-file': {'foreground': p['fg'], 'weight': Symbol('bold')},
            'doom-modeline-buffer-path': {'foreground': p['muted']},
            'doom-modeline-buffer-project-root': {'foreground': p['func'], 'weight': Symbol('bold')},
            'solaire-default-face': {'foreground': p['fg'], 'background': p['panel']},
            'solaire-hl-line-face': {'background': p['line'], 'extend': True},
            'solaire-mode-line-face': {'foreground': p['fg'], 'background': p['panel'], 'box': False},
            'solaire-mode-line-inactive-face': {'foreground': p['muted'], 'background': p['line'], 'box': False},
        }
        for face in ('eglot-inlay-hint', 'lsp-inlay-hint-face', 'lsp-lens-face', 'lsp-inlay-hint-type-face', 'lsp-inlay-hint-parameter-face'):
            faces[face] = {'foreground': p['comment'], 'slant': Symbol('normal')}
        for severity, role in [('error', 'error'), ('warning', 'warning'), ('note', 'info')]:
            underline = {'style': Symbol('wave'), 'color': p[role]}
            faces[f'flymake-{severity}'] = {'underline': underline}
            faces[f'flycheck-{"info" if severity == "note" else severity}'] = {'underline': underline}
        for level, role in enumerate(['func', 'type', 'keyword', 'constant', 'func', 'type', 'keyword', 'constant'], 1):
            faces[f'org-level-{level}'] = {'foreground': p[role], 'weight': Symbol('bold')}
        for index, name in enumerate(['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']):
            faces[f'term-color-{name}'] = {'foreground': ansi[index], 'background': ansi[index]}
            faces[f'ansi-color-{name}'] = {'foreground': ansi[index], 'background': ansi[index]}
            faces[f'ansi-color-bright-{name}'] = {'foreground': ansi[index + 8], 'background': ansi[index + 8]}
        for index, color in enumerate(ansi):
            faces[f'vterm-color-{index}'] = {'foreground': color, 'background': color}
        return faces


    def emacs_header(name, data, source):
        return [f';;; {name}-theme.el --- {data["name"]} colors -*- lexical-binding: t; -*-',
                ';; SPDX-License-Identifier: MIT', ';; Author: librerob',
                ';; URL: https://github.com/librerob/verdelle', ';; Keywords: faces, themes',
                ';;; Commentary:', f';; Generated from {source} by tools/build.py.',
                ';;; Code:', '']


    def generate(variant):
        suffix = '-light' if variant == 'light' else ''
        source = f'palette/{variant}.json'
        data = palettes[variant]
        p, ansi = data['colors'], data['ansi']
        slug = 'verdelle' + suffix

        base16_roles = ['bg', 'line', 'selection', 'comment', 'muted', 'fg', 'bright', 'bright',
                        'error', 'constant', 'type', 'string', None, 'func', 'keyword', 'warning']
        base16 = {f'base{i:02X}': p[role] if role else ansi[6] for i, role in enumerate(base16_roles)}
        metadata = {'system': 'base16', 'name': data['name'], 'author': 'librerob', 'variant': variant}
        modern = [f'{key}: {json.dumps(value)}' for key, value in metadata.items()] + ['palette:']
        modern += [f'  {key}: "{color}"' for key, color in base16.items()]
        write(f'ports/base16/{slug}.yaml', '\n'.join(modern))
        legacy = [f'scheme: "{data["name"]}"', 'author: "librerob"']
        legacy += [f'{key}: "{color[1:]}"' for key, color in base16.items()]
        write(f'ports/base16/legacy/{slug}.yaml', '\n'.join(legacy))

        vscode = json.loads(generated[f'ports/vscode/themes/{slug}-color-theme.json'])
        settings = [{'settings': {
            'foreground': p['fg'], 'background': p['bg'], 'caret': p['cursor'],
            'selection': p['selection'], 'selectionForeground': p['selection_fg'],
            'lineHighlight': p['line'], 'invisibles': p['subdued'],
            'findHighlight': p['search_bg'], 'findHighlightForeground': p['search_fg'],
            'gutter': p['panel'], 'gutterForeground': p['comment'],
        }}]
        for token in vscode['tokenColors']:
            settings.append({'scope': ', '.join(token['scope']), 'settings': token['settings']})
        settings.append({'scope': 'invalid', 'settings': {'foreground': p['error'], 'fontStyle': 'underline'}})
        write(f'ports/bat/{data["name"]}.tmTheme',
              plistlib.dumps({'name': data['name'], 'settings': settings}, sort_keys=False).decode('utf-8'))

        colorls_roles = {
            'unrecognized_file': 'muted', 'recognized_file': 'fg', 'executable_file': 'focus', 'dir': 'func',
            'dead_link': 'error', 'link': 'type', 'socket': 'constant', 'blockdev': 'constant',
            'chardev': 'constant', 'hidden': 'muted', 'hidden_dir': 'func',
            'write': 'keyword', 'read': 'type', 'exec': 'focus', 'no_access': 'error',
            'day_old': 'comment', 'hour_old': 'muted', 'no_modifier': 'comment',
            'file_large': 'warning', 'file_medium': 'constant', 'file_small': 'fg',
            'report': 'muted', 'user': 'constant', 'tree': 'border', 'empty': 'comment',
            'error': 'error', 'normal': 'fg', 'inode': 'comment', 'addition': 'focus',
            'modification': 'type', 'deletion': 'error', 'untracked': 'warning', 'unchanged': 'comment',
        }
        # Rainbow 3 converts HEX requests to its coarse 256-color cube. ANSI names
        # preserve the colors of the matching Verdelle terminal preset instead.
        neutral = 'white' if variant == 'dark' else 'default'
        colorls_ansi = {'fg': 'default', 'muted': neutral, 'comment': neutral, 'border': neutral,
                       'func': 'cyan', 'type': 'blue', 'constant': 'magenta', 'keyword': 'yellow',
                       'error': 'red', 'warning': 'yellow', 'focus': 'green'}
        write(f'ports/colorls/{variant}_colors.yaml',
              f'# {data["name"]}. Use with the matching terminal preset.\n'
              + '\n'.join(f'{key}: "{colorls_ansi[role]}"' for key, role in colorls_roles.items()))

        faces = emacs_faces(p, ansi)
        vector = '[' + ' '.join(json.dumps(color) for color in ansi[:8]) + ']'
        lines = emacs_header(slug, data, source)
        lines += [f'(deftheme {slug} "{data["name"]} colors for a truecolor display.")', '',
                  f"(custom-theme-set-faces '{slug}"]
        lines += [f" '({face} ((t {lisp(attrs)})))" for face, attrs in faces.items()]
        lines[-1] += ')'
        lines += ['', f"(custom-theme-set-variables '{slug}",
                  f" '(frame-background-mode '{variant})", f" '(ansi-color-names-vector {vector}))",
                  '', f"(provide-theme '{slug})", f';;; {slug}-theme.el ends here']
        write(f'ports/emacs/{slug}-theme.el', '\n'.join(lines))

        doom_name = 'doom-' + slug
        defs = {
            'bg': 'bg', 'fg': 'fg', 'bg-alt': 'panel', 'fg-alt': 'muted',
            'base0': 'panel', 'base1': 'bg', 'base2': 'line', 'base3': 'float',
            'base4': 'border', 'base5': 'comment', 'base6': 'muted', 'base7': 'fg', 'base8': 'bright',
            'grey': 'comment', 'red': 'error', 'orange': 'keyword', 'green': 'func', 'teal': 'hint',
            'yellow': 'warning', 'blue': 'type', 'dark-blue': 'type', 'magenta': 'constant',
            'violet': 'constant', 'cyan': 'info', 'dark-cyan': 'info',
            'highlight': 'focus', 'selection': 'selection', 'region': 'selection', 'vertical-bar': 'border',
            'builtin': 'type', 'comments': 'comment', 'doc-comments': 'comment', 'constants': 'constant',
            'functions': 'func', 'methods': 'func', 'keywords': 'keyword', 'operators': 'operator',
            'type': 'type', 'strings': 'string', 'variables': 'variable', 'numbers': 'constant',
            'error': 'error', 'warning': 'warning', 'success': 'focus',
            'vc-added': 'focus', 'vc-deleted': 'error', 'vc-modified': 'type',
        }
        lines = emacs_header(doom_name, data, source)
        lines += ["(require 'doom-themes)", '', f'(def-doom-theme {doom_name}',
                  f'  "{data["name"]} colors for doom-themes."', '  (']
        lines += [f'   ({key} \'("{p[role]}"))' for key, role in defs.items()]
        lines += ['  )', '  (']
        for face, attrs in faces.items():
            values = ' '.join(f':{key} ' + ("'" if isinstance(value, (Symbol, dict)) else '') + lisp(value)
                              for key, value in attrs.items())
            lines.append(f'   ({face} {values})')
        lines += ['  )', f"  ((frame-background-mode ''{variant})", f'   (ansi-color-names-vector {vector})))',
                  '', f';;; {doom_name}-theme.el ends here']
        write(f'ports/doom-emacs/{doom_name}-theme.el', '\n'.join(lines))


    for variant in ('dark', 'light'):
        generate(variant)
    return result
