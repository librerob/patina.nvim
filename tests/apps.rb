# Parse the YAML ports with Ruby's YAML reader and exercise colorls itself.
require 'json'
require 'yaml'
require 'set'
require 'tmpdir'
require 'fileutils'
require 'open3'

ROOT = File.expand_path('..', __dir__)

def check(condition, message)
  raise message unless condition
end

def luminance(hex)
  hex.delete_prefix('#').scan(/../).map { |c| c.to_i(16) / 255.0 }
     .map { |v| v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055)**2.4 }
     .zip([0.2126, 0.7152, 0.0722]).sum { |v, weight| v * weight }
end

def contrast(a, b)
  low, high = [luminance(a), luminance(b)].sort
  (high + 0.05) / (low + 0.05)
end

keys = %w[unrecognized_file recognized_file executable_file dir dead_link link socket blockdev chardev
          hidden hidden_dir write read exec no_access day_old hour_old no_modifier file_large file_medium
          file_small report user tree empty error normal inode addition modification deletion untracked unchanged]
%w[dark light].each do |variant|
  suffix = variant == 'light' ? '-light' : ''
  palette = JSON.parse(File.read(File.join(ROOT, "palette/#{variant}.json")))
  p = palette.fetch('colors')
  base16 = YAML.safe_load(File.read(File.join(ROOT, "ports/base16/verdelle#{suffix}.yaml")))
  legacy = YAML.safe_load(File.read(File.join(ROOT, "ports/base16/legacy/verdelle#{suffix}.yaml")))
  check(base16.fetch('system') == 'base16' && base16.fetch('variant') == variant, 'Base16 metadata')
  colors = base16.fetch('palette')
  check(colors.keys.to_set == (0...16).map { |i| format('base%02X', i) }.to_set, 'Base16 slot coverage')
  colors.each do |key, color|
    check(p.values.include?(color) || palette.fetch('ansi').include?(color), "Off-palette Base16 #{key}")
    check(legacy.fetch(key) == color.delete_prefix('#'), "Legacy Base16 drift: #{key}")
  end
  { 'base00' => 'bg', 'base03' => 'comment', 'base05' => 'fg',
    'base0B' => 'string', 'base0D' => 'func', 'base0E' => 'keyword' }.each do |key, role|
    check(colors.fetch(key) == p.fetch(role), "Base16 role mismatch: #{key}")
  end

  colorls = YAML.safe_load(File.read(File.join(ROOT, "ports/colorls/#{variant}_colors.yaml")))
  check(colorls.keys.to_set == keys.to_set, 'colorls key coverage')
  colorls.each do |key, name|
    slots = { 'red' => 1, 'green' => 2, 'yellow' => 3, 'blue' => 4, 'magenta' => 5, 'cyan' => 6, 'white' => 7 }
    color = name == 'default' ? p.fetch('fg') : palette.fetch('ansi').fetch(slots.fetch(name))
    %w[bg panel line float].each { |surface| check(contrast(color, p.fetch(surface)) >= 4.5, "Low-contrast colorls #{key}") }
  end
  check(colorls.fetch('dir') == 'cyan' && colorls.fetch('recognized_file') == 'default', 'colorls semantic roles')
end

if ARGV.include?('--colorls')
  Dir.mktmpdir('verdelle-colorls-') do |home|
    config = File.join(home, '.config/colorls')
    FileUtils.mkdir_p(config)
    FileUtils.cp(Dir[File.join(ROOT, 'ports/colorls/*.yaml')], config)
    fixture = File.join(home, 'fixture')
    FileUtils.mkdir_p(File.join(fixture, 'documents'))
    File.write(File.join(fixture, 'example.txt'), 'Verdelle')
    %w[dark light].each do |variant|
      output, error, status = Open3.capture3({ 'HOME' => home, 'TERM' => 'xterm-256color', 'COLORTERM' => 'truecolor' },
                                            'colorls', '--color=always', "--#{variant}", fixture)
      check(status.success?, "colorls #{variant} failed: #{error}")
      check(output.include?('example.txt') && output.include?('documents'), 'colorls listing is incomplete')
      check(output.include?("\e[36m"), "colorls did not use the custom ANSI directory color: #{output.inspect}")
    end
  end
end
puts 'Base16 and colorls YAML passed; native colorls passed when requested'
