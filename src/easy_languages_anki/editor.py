import os
import subprocess
import tempfile


def drop_user_into_editor(text):
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode="w+t") as f:
        f.write(text)
        f.close()

        editor = os.environ.get("EDITOR", "vim")
        subprocess.call([editor, f.name])

        f = open(f.name)
        edited_text = f.read()
        f.close()
        os.unlink(f.name)

        return edited_text
