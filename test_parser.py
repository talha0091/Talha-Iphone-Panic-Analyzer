import re
import sys

# Mocking parts of app.py to run just the finalize_diagnostic_render_pass
from app import MasterWorkspaceContainer, BITMASK_REGISTRY

class MockTextWidget:
    def __init__(self):
        self.state = "normal"
        self.content = ""

    def configure(self, state):
        self.state = state

    def delete(self, start, end):
        self.content = ""

    def insert(self, start, text):
        self.content += text

    def get(self, start, end):
        return self.content

class MockWorkspace:
    def __init__(self):
        # Override init to not start GUI or threads
        self.txt_simple_verdict = MockTextWidget()
        self.c_neon_blue = "#00D2FF"
        # We can't easily mock btn_scan without errors, so let's mock it
        class MockButton:
            def configure(self, **kwargs):
                pass
        self.btn_scan = MockButton()
        # Bind the original function
        self.finalize_diagnostic_render_pass = MasterWorkspaceContainer.finalize_diagnostic_render_pass.__get__(self, MockWorkspace)

    def render_invalid_log_parse(self):
        self.txt_simple_verdict.configure(state="normal")
        self.txt_simple_verdict.delete("1.0", "end")
        self.txt_simple_verdict.insert("1.0", "⚠️ PARSING ERROR: No valid hardware register bitmask tracking signatures found in this log.")
        self.txt_simple_verdict.configure(state="disabled")

    def clear_workbench_displays(self):
        self.txt_simple_verdict.configure(state="normal")
        self.txt_simple_verdict.delete("1.0", "end")
        self.txt_simple_verdict.insert("1.0", "[ WORKBENCH READY -> INITIALIZE DATA SCAN PATHWAY ]")
        self.txt_simple_verdict.configure(state="disabled")

# Test 1: Single failure
log_single = '{"panicString" : "panic(cpu 1 caller 0xfffffff011111111): AOP Panic - sensor array is 0x400\\n"}'
# Test 2: Dual failure
log_dual = '{"panicString" : "panic(cpu 2 caller 0xfffffff022222222): AOP Panic - sensor array is 0x4800\\n"}'
# Test 3: Triple failure
log_triple = '{"panicString" : "panic(cpu 0 caller 0xfffffff033333333): AOP Panic - sensor array is 0x1C0000\\n"}'
# Test 4: Corrupted data format (should hit graceful error)
log_corrupted = '{"panicString" : "panic(cpu 0 caller 0xfffffff033333333): AOP Panic - sensor array is corrupted_garbage_\\x80\\n"}'
# Test 5: String matching fallback
log_string_match = '{"panicString" : "panic(cpu 1 caller 0xfffffff011111111): SMC BSC failure\\n"}'

workspace = MockWorkspace()

def run_test(name, log_data, expected_text_in_output):
    print(f"Running test: {name}")
    try:
        workspace.finalize_diagnostic_render_pass(log_data)
        output = workspace.txt_simple_verdict.content
        if expected_text_in_output in output:
            print("  ✅ Passed")
            return True
        else:
            print(f"  ❌ Failed")
            print(f"     Expected: {expected_text_in_output}")
            print(f"     Got: {output}")
            return False
    except Exception as e:
        print(f"  ❌ Failed with exception: {e}")
        return False

def main():
    results = []
    results.append(run_test("Single Failure", log_single, BITMASK_REGISTRY["0x400"]))
    results.append(run_test("Dual Failure", log_dual, BITMASK_REGISTRY["0x4800"]))
    results.append(run_test("Triple Failure", log_triple, BITMASK_REGISTRY["0x1C0000"]))
    results.append(run_test("Corrupted Data", log_corrupted, "⚠️ PARSING ERROR: No valid hardware register bitmask tracking signatures found in this log."))
    results.append(run_test("String Match", log_string_match, BITMASK_REGISTRY["SMC BSC failure"]))

    if all(results):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
