#include <Python.h>
#include <structmember.h>
#include "nabto_client_api.h"

static PyObject* NabtoError = NULL;

typedef struct {
    PyObject_HEAD
    nabto_handle_t session;
} SessionObject;

typedef struct {
    PyObject_HEAD
    nabto_tunnel_t tunnel;
} TunnelObject;

// Session
static PyObject* py_nabtoStartup(PyObject* self, PyObject *args);
static PyObject* py_nabtoShutdown(PyObject* self, PyObject *args);
static PyObject* py_nabtoVersionString(PyObject* self, PyObject *args);
static void      Session_dealloc(SessionObject *self);
static PyObject* Session_open(SessionObject* self, PyObject *args);
static PyObject* Session_close(SessionObject* self, PyObject *Py_UNUSED(ignored));
static PyObject* Session_rpcSetDefaultInterface(SessionObject* self, PyObject *args);
static PyObject* Session_rpcInvoke(SessionObject* self, PyObject *args);
// Tunnel
static void      Tunnel_dealloc(TunnelObject *self);
static PyObject* Tunnel_openTcp(TunnelObject* self, PyObject* args);
static PyObject* Tunnel_close(TunnelObject* self, PyObject* args);
static PyObject* Tunnel_status(TunnelObject* self, PyObject *Py_UNUSED(ignored));
// Profile
static PyObject* py_nabtoCreateSelfSignedProfile(PyObject* self, PyObject *args);
static PyObject* py_nabtoRemoveProfile(PyObject* self, PyObject *args);
static PyObject* py_nabtoGetFingerprint(PyObject* self, PyObject *args);

static PyMethodDef NabtoMethods[] = {
    {
        "nabtoStartup", py_nabtoStartup, METH_VARARGS,
        "Initializes the Nabto client API"
    },
    {
        "nabtoShutdown", py_nabtoShutdown, METH_NOARGS,
        "Terminates the Nabto client API"
    },
    {
        "nabtoVersionString", py_nabtoVersionString, METH_NOARGS,
        "Get the underlying C libs Nabto software version (major.minor.patch[-prerelease tag]+build)"
    },
    {
        "nabtoCreateSelfSignedProfile", py_nabtoCreateSelfSignedProfile, METH_VARARGS,
        "Creates a Nabto self signed profile. The identity of such certificate cannot be trusted but the fingerprint of the certificate can be trusted in the device. After the profile has been created it can be used in the open session function."
    },
    {
        "nabtoRemoveProfile", py_nabtoRemoveProfile, METH_VARARGS,
        "Remove profile certificate for given id."
    },
    {
        "nabtoGetFingerprint", py_nabtoGetFingerprint, METH_VARARGS,
        "Retrieve public key fingerprint for profile with specified id."
    },
    {
        NULL, NULL, 0, NULL
    }
};

static PyMethodDef SessionMethods[] = {
    {
        "open", (PyCFunction) Session_open, METH_VARARGS, 
        "Starts a new Nabto session as context for RPC, stream or tunnel invocation using the specified profile."
    },
    {
        "close", (PyCFunction) Session_close, METH_VARARGS,
        "Closes the specified Nabto session and frees internal ressources."
    },
    {
        "rpcSetDefaultInterface", (PyCFunction) Session_rpcSetDefaultInterface, METH_VARARGS,
        "Sets the default RPC interface to use when later invoking Session.rpcInvoke()."
    },
    {
        "rpcInvoke", (PyCFunction) Session_rpcInvoke, METH_VARARGS,
        "Retrieves data synchronously from specified nabto:// URL on specified session"
    },
    {
        NULL, NULL, 0, NULL
    }
};

static PyMethodDef TunnelMethods[] = {
    {
        "openTcp", (PyCFunction) Tunnel_openTcp, METH_VARARGS,
        "Opens a TCP tunnel to a remote server through a Nabto enabled device."
    },
    {
        "close", (PyCFunction) Tunnel_close, METH_NOARGS,
        "Closes an open tunnel."
    },
    {
        "status", (PyCFunction) Tunnel_status, METH_NOARGS,
        "Returns the current state of the tunnel."
    },
    {
        NULL, NULL, 0, NULL
    }
};

static PyTypeObject SessionType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "nabto.Session",
    .tp_doc = "Session object",
    .tp_basicsize = sizeof(SessionObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor) Session_dealloc,
    .tp_methods = SessionMethods,
};

static PyTypeObject TunnelType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "nabto.Tunnel",
    .tp_doc = "Tunnel object",
    .tp_basicsize = sizeof(TunnelObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor) Tunnel_dealloc,
    .tp_methods = TunnelMethods,
};

static struct PyModuleDef nabtoModule = {
    PyModuleDef_HEAD_INIT,
    "nabto",
    "Python interface for the Nabto client C API",
    -1,
    NabtoMethods
};

PyMODINIT_FUNC PyInit_nabto(void) {
    if (PyType_Ready(&SessionType) < 0) {
        return NULL;
    }
    if (PyType_Ready(&TunnelType) < 0) {
        return NULL;
    }

    PyObject* module = PyModule_Create(&nabtoModule);

    NabtoError = PyErr_NewException("nabto.NabtoError", NULL, NULL);
    PyModule_AddObject(module, "NabtoError", NabtoError);

    Py_INCREF(&SessionType);
    if (PyModule_AddObject(module, "Session", (PyObject*)&SessionType) < 0) {
        Py_DECREF(&SessionType);
        Py_DECREF(module);
        return NULL;
    }

    Py_INCREF(&TunnelType);
    if (PyModule_AddObject(module, "Tunnel", (PyObject*)&TunnelType) < 0) {
        Py_DECREF(&TunnelType);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}

// Session API

static PyObject* py_nabtoStartup(PyObject* self, PyObject *args) {
    char *homeDir = NULL;
    if (!PyArg_ParseTuple(args, "s", &homeDir)) {
        return NULL;
    }

    nabto_status_t st = nabtoStartup(homeDir);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* py_nabtoShutdown(PyObject* self, PyObject *args) {
    nabto_status_t st = nabtoShutdown();
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* py_nabtoVersionString(PyObject* self, PyObject *args) {
    char* version;
    nabto_status_t st = nabtoVersionString(&version);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    PyObject* result = PyUnicode_FromString(version);
    nabtoFree(version);
    return result;
}

static void Session_dealloc(SessionObject *self) {
    if (self->session != NULL) {
        nabto_status_t st = nabtoCloseSession(self->session);
        if (st != NABTO_OK) {
            PyErr_SetString(NabtoError, nabtoStatusStr(st));
            return;
        }
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* Session_open(SessionObject* self, PyObject *args) {
    char* id = NULL;
    char* password = NULL;
    if (!PyArg_ParseTuple(args, "ss", &id, &password)) {
        return NULL;
    }
    nabto_status_t st = nabtoOpenSession(&self->session, id, password);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Session_close(SessionObject* self, PyObject *Py_UNUSED(ignored)) {
    nabto_handle_t session = self->session;
    self->session = NULL;
    nabto_status_t st = nabtoCloseSession(session);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Session_rpcSetDefaultInterface(SessionObject* self, PyObject *args) {
    char* interfaceDefinition = NULL;
    char* err = NULL;
    if (!PyArg_ParseTuple(args, "s", &interfaceDefinition)) {
        return NULL;
    }
    nabto_status_t st = nabtoRpcSetDefaultInterface(self->session, interfaceDefinition, &err);
    if (st != NABTO_OK) {
        if (st == NABTO_FAILED_WITH_JSON_MESSAGE) {
            PyErr_SetString(NabtoError, err);
            nabtoFree(err);
            return NULL;
        }
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject* Session_rpcInvoke(SessionObject* self, PyObject *args) {
    char* url = NULL;
    char* response = NULL;
    if (!PyArg_ParseTuple(args, "s", &url)) {
        return NULL;
    }
    nabto_status_t st = nabtoRpcInvoke(self->session, url, &response);
    PyObject* result = PyUnicode_FromString(response);
    nabtoFree(response);
    if (st != NABTO_OK) {
        if (st == NABTO_FAILED_WITH_JSON_MESSAGE) {
            PyErr_SetObject(NabtoError, result);
            return NULL;
        }
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }
    return result;
}

// Tunnel API

static void Tunnel_dealloc(TunnelObject *self) {
    if (self->tunnel != NULL) {
        nabto_status_t st = nabtoTunnelClose(self->tunnel);
        if (st != NABTO_OK) {
            PyErr_SetString(NabtoError, nabtoStatusStr(st));
            return;
        }
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* Tunnel_openTcp(TunnelObject* self, PyObject* args) {
    PyObject* session = NULL;
    long localPort = 0;
    char* nabtoHost = NULL;
    char* remoteHost = NULL;
    long remotePort = 0;
    if (!PyArg_ParseTuple(args, "Olssl", &session, &localPort, &nabtoHost, &remoteHost, &remotePort)) {
        return NULL;
    }
    if (!PyObject_IsInstance(session, (PyObject*)&SessionType)) {
        PyErr_SetString(PyExc_TypeError, "a nabto.Session object is required");
        return NULL;
    }
    nabto_handle_t session_obj = ((SessionObject*)session)->session;
    
    // start tunnel operations
    nabto_status_t st = nabtoTunnelOpenTcp(&self->tunnel, session_obj, localPort, nabtoHost, remoteHost, remotePort);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    nabto_tunnel_state_t tunnelState = NTCS_CLOSED;
    while (tunnelState < NTCS_LOCAL) {
        st = nabtoTunnelInfo(self->tunnel, NTI_STATUS, sizeof(tunnelState), &tunnelState);
        if (st != NABTO_OK) {
            PyErr_SetString(NabtoError, nabtoStatusStr(st));
            return NULL;
        }
        if (tunnelState == NTCS_CLOSED) {
            PyErr_SetString(NabtoError, "Could not open tunnel");
            return NULL;
        }
        usleep(50 * 1000); //50ms
    }
    long port = 0;
    st = nabtoTunnelInfo(self->tunnel, NTI_PORT, sizeof(port), &port);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }    

    return PyLong_FromLong(port);
}

static PyObject* Tunnel_close(TunnelObject* self, PyObject* args) {
    nabto_tunnel_t tunnel = self->tunnel;
    self->tunnel = NULL;
    nabto_status_t st = nabtoTunnelClose(tunnel);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Tunnel_status(TunnelObject* self, PyObject *Py_UNUSED(ignored)) {
    nabto_tunnel_state_t state = NTCS_CLOSED;
    if (self->tunnel != NULL) {
        nabto_status_t st = nabtoTunnelInfo(self->tunnel, NTI_STATUS, sizeof(state), &state);
        if (st != NABTO_OK) {
            PyErr_SetString(NabtoError, nabtoStatusStr(st));
            return NULL;
        }
    }

    return PyLong_FromLong(state);
}

static PyObject* py_nabtoCreateSelfSignedProfile(PyObject* self, PyObject *args) {
    char* id = NULL;
    char* password = NULL;
    if (!PyArg_ParseTuple(args, "ss", &id, &password)) {
        return NULL;
    }
    nabto_status_t st = nabtoCreateSelfSignedProfile(id, password);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* py_nabtoRemoveProfile(PyObject* self, PyObject *args) {
    char* id = NULL;
    if (!PyArg_ParseTuple(args, "s", &id)) {
        return NULL;
    }
    nabto_status_t st = nabtoRemoveProfile(id);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* py_nabtoGetFingerprint(PyObject* self, PyObject *args) {
    char* id = NULL;
    char fingerprint[16];
    if (!PyArg_ParseTuple(args, "s", &id)) {
        return NULL;
    }
    nabto_status_t st = nabtoGetFingerprint(id, fingerprint);
    if (st != NABTO_OK) {
        PyErr_SetString(NabtoError, nabtoStatusStr(st));
        return NULL;
    }
    char fp[33] = {'\0'};
    const char* table = "0123456789abcdef";
    for(int i = 0; i < 16; i++) {
        fp[2 * i] = table[(unsigned char)(fingerprint[i]) >> 4];
        fp[2 * i + 1] = table[(unsigned char)(fingerprint[i] & 0x0f)];
    }

    return PyUnicode_FromString(fp);
}
