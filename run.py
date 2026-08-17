import os
import sys
from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = os.path.abspath("app.py")
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
