from typing import Tuple
from langchain_core.tools import tool
import subprocess
from common.utils.logger import log


@tool
def run_bash_cmd(command: str) -> Tuple[str, str]:
    """Runs a bash command.

    Args:
      command: The command to exectute.

    Returns:
      Tuple[str, str]: A tuple, with the first value being the output and the second the error, if there is one.
    """

    log(f"run_bash_cmd START. command: {command}.")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = result.stdout.decode("utf-8").strip()
        error = result.stderr.decode("utf-8").strip()

        log(f"run_bash_cmd END.")

        return output, error
    except subprocess.CalledProcessError as e:
        log(f"run_bash_cmd ERROR. command: {command}, error: {str(e)}")
        return None, str(e)
