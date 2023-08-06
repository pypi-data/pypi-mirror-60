from ifile import api
from ifile.api import errors    # noqa
from ifile.api import file as file_api, client as client_api

api.blueprint.add_url_rule(
    '/version',
    view_func=api.get_version)

api.blueprint.add_url_rule(
    '/files',
    view_func=file_api.Files.as_view('files'))

api.blueprint.add_url_rule(
    '/files/<int:id>',
    view_func=file_api.File.as_view('file'))

api.blueprint.add_url_rule(
    '/downloader/files/<int:id>',
    view_func=file_api.FileDownloader.as_view('downloader_file'))

api.blueprint.add_url_rule(
    '/remotefiles',
    view_func=file_api.RemoteFiles.as_view('remotefile'))

api.blueprint.add_url_rule(
    '/clients',
    view_func=client_api.Clients.as_view('clients'))

api.blueprint.add_url_rule(
    '/clients/<int:id>',
    view_func=client_api.Client.as_view('client'))
