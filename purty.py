import os
import os.path
import sublime
import sublime_plugin
import subprocess


class PurtyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        purty = find_purty(self.view)

        if purty == None:
            return

        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)

        stdout, stderr = subprocess.Popen(
            [purty, '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=os.name=="nt").communicate(input=bytes(content, 'UTF-8'))

        if stderr.strip():
            open_panel(self.view, stderr.strip().decode())
        else:
            self.view.replace(edit, region, stdout.decode('UTF-8'))
            self.view.window().run_command("hide_panel", {"panel": "output.purty"})


class PurtyOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        scope = view.scope_name(0)
        if scope.find('source.purescript') != -1 and needs_format(view):
            view.run_command('purty')


def needs_format(view):
    settings = sublime.load_settings('purty-on-save.sublime-settings')
    on_save = settings.get('on_save', True)

    if isinstance(on_save, bool):
        return on_save

    if isinstance(on_save, dict):
        path = view.file_name()
        included = is_included(on_save, path)
        excluded = is_excluded(on_save, path)
        if isinstance(included, bool) and isinstance(excluded, bool):
            return included and not excluded

    open_panel(view, invalid_settings)
    return False


def is_included(on_save, path):
    if "including" in on_save:
        if not isinstance(on_save.get("including"), list):
            return None

        for string in on_save.get("including"):
            if string in path:
                return True

        return False

    return True


def is_excluded(on_save, path):
    if "excluding" in on_save:
        if not isinstance(on_save.get("excluding"), list):
            return None

        for string in on_save.get("excluding"):
            if string in path:
                return True

        return False

    return False


def find_purty(view):
    settings = sublime.load_settings('purty-on-save.sublime-settings')
    given_path = settings.get('absolute_path')
    if given_path != None and given_path != '':
        if isinstance(given_path, str) and os.path.isabs(given_path) and os.access(given_path, os.X_OK):
            return given_path

        open_panel(view, bad_absolute_path)
        return None

    

    exts = os.environ['PATHEXT'].lower().split(os.pathsep) if os.name == 'nt' else ['']
    for directory in os.environ['PATH'].split(os.pathsep):
        for ext in exts:
            path = os.path.join(directory, 'purty' + ext)
            if os.access(path, os.X_OK):
                return path

    open_panel(view, cannot_find_purty())
    return None


def open_panel(view, content):
    window = view.window()
    panel = window.create_output_panel("purty")
    panel.set_read_only(False)
    panel.run_command('erase_view')
    panel.run_command('append', {'characters': content})
    panel.set_read_only(True)
    window.run_command("show_panel", {"panel": "output.purty"})


def cannot_find_purty():
    return """-- PURTY NOT FOUND ----------------------------------------------------
I tried run purty, but I could not find it on your computer.
-----------------------------------------------------------------------
NOTE: Your PATH variable led me to check in the following directories:
    """ + '\n    '.join(os.environ['PATH'].split(os.pathsep)) + """
But I could not find `purty` in any of them. Please let me know
at https://github.com/aggressivepixels/purty-on-save/issues if this does
not seem correct!
"""


invalid_settings = """-- INVALID SETTINGS ---------------------------------------------------
The "on_save" field in your settings is invalid.
For help, check out the section on including/excluding files within:
  https://github.com/aggressivepixels/purty-on-save/blob/master/README.md
-----------------------------------------------------------------------
"""


bad_absolute_path = """-- INVALID SETTINGS ---------------------------------------------------
The "absolute_path" field in your settings is invalid.
I need the following Python expressions to be True with the given path:
    os.path.isabs(absolute_path)
    os.access(absolute_path, os.X_OK)
Is the path correct? Do you need to run "chmod +x" on the file?
-----------------------------------------------------------------------
"""
