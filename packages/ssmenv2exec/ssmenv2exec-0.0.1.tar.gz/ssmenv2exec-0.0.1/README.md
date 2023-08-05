# ssmenv2exec

Populate environment variables from AWS Systems Manager Parameter Store
parameters before executing a process.

This allows application configuration to be stored in SSM rather than on
the EC2 instance or Docker container.

# Usage

    pip install ssmenv2exec

Now you can use the `ssmenv2exec` script from the command line to execute your process
and have the environment populated from an AWS SSM Parameter store path.

For example, in parameter store you can create parameters using a common path.

    /app/myapp/DB_USER
    /app/myapp/DB_PASS
    /app/myapp/DB_URL
    /app/myapp/SECRET_KEY

Then you can use `ssmenv2exec` to execute your program and the initial environment
will contain values for `DB_USER`, `DB_PASS`, `DB_URL` and `SECRET_KEY`. If any of
those already exist as environment variables they will not be overridden.

    ssmenv2exec /app/myapp python app.py

`ssmenv2exec` will grab all parameters from the Parameter Store under the
`/app/myapp` path and pass those as environment variables to the process. An
`exec` call is used so that the process id (pid) remains consistent, which is
useful for containerized environments.
