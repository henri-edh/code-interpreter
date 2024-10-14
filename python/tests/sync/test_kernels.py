from e2b_code_interpreter.code_interpreter_sync import Sandbox


def test_create_new_kernel(sandbox: Sandbox):
    sandbox.create_code_context()


def test_independence_of_kernels(sandbox: Sandbox):
    context = sandbox.create_code_context()
    sandbox.run_code("x = 1")

    r = sandbox.run_code("x", context=context)
    assert r.error is not None
    assert r.error.value == "name 'x' is not defined"
