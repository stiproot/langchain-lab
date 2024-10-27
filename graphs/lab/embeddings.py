from agnt_smth.vectors import embed_file_system_contents

if __name__ == "__main__":
    import asyncio

    repo_path = "/Users/simon.stipcich/code/repo/xo-tasktree"

    asyncio.run(embed_file_system_contents(repo_path))
