from invoke import task


@task
def start(c):
    c.run('which python')

