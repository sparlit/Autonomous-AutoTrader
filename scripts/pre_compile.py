import compileall
import os
def pre_compile():
    print("🚀 Starting Pre-compilation Phase...")
    compileall.compile_dir('src/python', force=True)
    print("🏁 Pre-compilation phase finished.")
if __name__ == "__main__": pre_compile()
