import logging
import os
import sys
from typing import List, Mapping

import boto3
import botocore.exceptions

logger = logging.getLogger('ssmenv2exec.main')


def parse_ssm_params(params: List[Mapping], *, path_sep: str) -> Mapping[str, str]:
    return {
        param['Name'].rsplit(path_sep, maxsplit=1)[-1]: param['Value']
        for param in params
    }


def get_params_by_path(param_path: str, *, path_sep: str = '/') -> Mapping[str, str]:
    """Returns a mapping of parameters under the given path."""
    ssm_client = boto3.client('ssm')
    params = ssm_client.get_parameters_by_path(
        Path=param_path,
        WithDecryption=True,
    )
    if not params['Parameters']:
        logger.warning('No parameters found for path [%s]', param_path)
        return {}
    return parse_ssm_params(params['Parameters'], path_sep=path_sep)


def main() -> None:
    if len(sys.argv) < 3:
        print('Usage:')
        print('\tssmenv2env /app/cas/ java -jar some.jar')
        print('\tssmenv2env /app/foo python run.py\n')
        sys.exit(1)

    env = os.environ
    args = sys.argv[2:]
    param_path = sys.argv[1]

    try:
        params = get_params_by_path(param_path)
    except botocore.exceptions.ClientError as ce:
        logger.warning('Failed to get params from path: %s\n%s',
                       param_path, ce)
    else:
        for k, v in params.items():
            if k not in env:
                env[k] = v
            else:
                logger.warning('Env var [%s] already exists, skipping', k)

    os.execvpe(args[0], args, env)


if __name__ == '__main__':
    main()
