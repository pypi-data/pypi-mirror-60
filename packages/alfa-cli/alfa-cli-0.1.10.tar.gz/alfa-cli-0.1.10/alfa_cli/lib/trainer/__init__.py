from alfa_sdk.common.exceptions import AlfaConfigError
from alfa_sdk.common.session import Session, parse_response
from alfa_sdk.resources.meta import MetaUnit
from alfa_cli.common.exceptions import AlfaCliError
from alfa_cli.common.utils import load_or_parse
from alfa_cli.lib.runner import LocalRunner


def initialize_runners(obj, algorithm_id, environment_name):
    """
    """
    search_runner = None
    try:
        search_runner = LocalRunner(obj, algorithm_id, environment_name, "search")
    except AlfaConfigError:
        pass

    score_runner = None
    try:
        score_runner = LocalRunner(obj, algorithm_id, environment_name, "score")
    except AlfaConfigError:
        pass

    build_runner = None
    build_runner = LocalRunner(obj, algorithm_id, environment_name, "build")

    return {
        "search": search_runner,
        "score": score_runner,
        "build": build_runner,
    }


def fetch_build_configuration(build_configuration=None, algorithm_environment_id=None, tag=None):
    """
    """
    if build_configuration:
        build_configuration = load_or_parse(build_configuration)
    else:
        if not algorithm_environment_id or not tag:
            raise AlfaCliError(message="Failed to fetch build configuration.")

        meta_unit = MetaUnit(algorithm_environment_id, tag)
        if not meta_unit:
            raise AlfaCliError(message="Failed to fetch build configuration.")

        build_configurations = meta_unit.build_configurations
        if not build_configurations or len(build_configurations) < 1:
            raise AlfaCliError(message="Failed to fetch build configuration.")

        build_configuration = build_configurations[0]

    if not "algorithmEnvironmentId" in build_configuration:
        build_configuration["algorithmEnvironmentId"] = algorithm_environment_id
    if not "tag" in build_configuration:
        build_configuration["tag"] = tag

    return build_configuration


def fetch_data(data, build_configuration):
    """
    """
    if data:
        return load_or_parse(data)

    data_request = build_configuration.get("dataRequest")
    if not data_request:
        raise AlfaCliError(message="Failed to fetch data.")

    session = Session()
    return parse_response(
        session.http_session.request(
            data_request.get("url"),
            data_request.get("method"),
            params=data_request.get("qs"),
            json=data_request.get("body"),
        )
    )
