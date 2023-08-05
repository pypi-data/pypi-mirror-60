#include <Python.h>

const char *UnitTestFile =  "test_lexer.py";

/**
 * Run the unit tests, to test the library. This is the entry point of the dylib.
 * So the dylib can be executed and test itself. Useful for debugging.
 *
 * Inspired by: http://pythonextensionpatterns.readthedocs.io/en/latest/debugging/debug_in_ide.html.
 */
int main(int argc, const char *argv[]) {
    // Convert argv to a wchar_t-argv.
    wchar_t **wchar_argv = malloc(sizeof(wchar_t*)*argc);
    if (wchar_argv == 0) { Py_FatalError("failed to alloc memory"); }

    for (int i = 0; i < argc; i++) {
        PyObject *unicode = PyUnicode_FromString(argv[i]);
        if (unicode == 0) {
            Py_FatalError("failed to convert argument to python string");
        }

        size_t length = (size_t)PyUnicode_GetLength(unicode);
        wchar_argv[i] = (wchar_t*)malloc(sizeof(wchar_t)*(length+1));
        if (wchar_argv[i] == 0) { Py_FatalError("failed to alloc memory"); }
        memset(wchar_argv[i], 0, sizeof(wchar_t)*(length+1));
        if (PyUnicode_AsWideChar(unicode, wchar_argv[i], length) != length) {
            Py_FatalError("failed to convert python string to wide char string");
        }
    }

    Py_Initialize();
    PySys_SetArgv(1, wchar_argv);

    if (PyErr_Occurred()) {
        goto main_error;
    }

    PyObject *obj = Py_BuildValue("s", UnitTestFile);

    FILE *f = fopen(UnitTestFile, "r+");
    if(f == 0) {
        fprintf(stderr, "%s: failed to open file", UnitTestFile);
        goto main_error;
    }

    PyRun_SimpleFile(f, UnitTestFile);
    if (PyErr_Occurred()) {
        goto main_error_1;
    }

    Py_Finalize();
    if (PyErr_Occurred()) {
        goto main_error_1;
    }

    fclose(f);
    return 0;

    main_error_1:
        fclose(f);

    main_error:
        if (PyErr_Occurred()) {
            PyErr_Print();
            Py_Finalize();
        }
        return 1;
}
