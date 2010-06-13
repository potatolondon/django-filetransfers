from django.conf import settings
from django.utils.importlib import import_module
import mimetypes

UPLOAD_BACKEND = getattr(settings,
    'FILETRANSFERS_UPLOAD_BACKEND',
    'filetransfers.backends.default.prepare_upload')
DOWNLOAD_BACKEND = getattr(settings,
    'FILETRANSFERS_DOWNLOAD_BACKEND',
    'filetransfers.backends.default.serve_file')
PUBLIC_DOWNLOAD_URL_BACKEND = getattr(settings,
    'FILETRANSFERS_PUBLIC_DOWNLOAD_URL_BACKEND',
    'filetransfers.backends.default.public_download_url')

_backends_cache = {}

# Public API
def prepare_upload(request, url, private=False, backend=None):
    handler = _load_backend(backend, UPLOAD_BACKEND)
    result = handler(request, url, private=private)
    if isinstance(result, (tuple, list)):
        return result
    return result, {}

def serve_file(request, file, backend=None, save_as=False, content_type=None):
    # Backends are responsible for handling range requests.
    handler = _load_backend(backend, DOWNLOAD_BACKEND)
    filename = file.name.rsplit('/')[-1]
    if save_as is True:
        save_as = filename
    if not content_type:
        content_type = mimetypes.guess_type(filename)[0]
    return handler(request, file, save_as=save_as, content_type=content_type)

def public_download_url(file, backend=None):
    handler = _load_backend(backend, PUBLIC_DOWNLOAD_URL_BACKEND)
    return handler(file)

# Internal utilities
def _load_backend(backend, default_backend):
    if backend is None:
        backend = default_backend
    if backend not in _backends_cache:
        module_name, func_name = backend.rsplit('.', 1)
        _backends_cache[backend] = getattr(import_module(module_name), func_name)
    return _backends_cache[backend]
