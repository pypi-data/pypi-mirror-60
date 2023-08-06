import click
import os
from .gitcd import Gitcd

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
AUTOCOMPLETE_ACTIVATION_BASH = "eval \"$(_GITCD_COMPLETE=source gitcd)\""
AUTOCOMPLETE_ACTIVATION_ZSH = "eval \"$(_GITCD_COMPLETE=source_zsh gitcd)\""

git = Gitcd()
git.read_repo_index()

def get_repo_names(ctx, args, incomplete):
    return [k.replace(" ", "\ ") for k in git.get_repo_index().keys() if incomplete in k]

@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("-i", "--index", is_flag=True, help="index all the local repo")
@click.option("-u", "--update", is_flag=True, help="update the local repo index")
@click.option("-p", "--path", type=click.Path(), required=False, help="only find local repo under this path")
@click.option("-a", "--autocomplete", is_flag=True, help="activate shell autocompletion")
@click.option("-s", "--shell", type=click.Choice(["bash", "zsh"]), help="specify the shell")
@click.argument("repo", required=False, autocompletion=get_repo_names)
def cli(ctx, index, update, autocomplete, shell, path, repo):
    '''
    gitcd [your-repo-name]

    Terminal tool for easy navigation to local git repository

    For more detail: please visit https://github.com/Doma1204/gitcd
    '''

    if index:
        click.echo("Start indexing")

        if path:
            result = git.generate_repo_index(path)
        else:
            result = git.generate_repo_index()

        if not result:
            click.secho("Fail to index", fg="red")
            raise click.ClickException("The path \"%s\" does not exist" % path)

        git.write_repo_index()

        click.secho("Finish indexing", fg="green")

        repo_names = git.get_repo_name_list()
        click.echo("%d local repository(s) found\n" % len(repo_names))
        click.echo("Repository found:")
        for name in repo_names:
            click.echo(name)
        return
    
    if update:
        click.echo("Start updating index")
        git.update_repo_index()
        git.write_repo_index()
        click.secho("Finish updating index", fg="green")
        return

    if autocomplete:
        env = shell if shell else os.environ["SHELL"]
        if env.find("bash") >= 0:
            env = "bash"
            rc = ".bashrc"
            activation = AUTOCOMPLETE_ACTIVATION_BASH
        elif env.find("zsh") >= 0:
            env = "zsh"
            rc = ".zshrc"
            activation = AUTOCOMPLETE_ACTIVATION_ZSH
        else:
            click.secho("Shell autocompletion is not compatible with %s" % env, fg="red")
            click.secho("Cannot set up shell autocompletion")
            raise click.ClickException("Only support bash and zsh shell")

        path = os.path.abspath(os.path.expanduser(os.path.join("~", rc)))
        if os.path.exists(path):
            with open(path, "r+") as file:
                if activation in file.read():
                    click.echo("Autocompletion already activated")
                else:
                    file.seek(0, 2)
                    file.write("\n" + activation)
                    file.close()
                    click.echo("Activate autocompletion")
                    os.system(os.environ["SHELL"])
        return

    if repo:
        dir = git.get_repo_dir(repo)
        if dir is None:
            raise click.ClickException("Repository \"%s\" not found" % repo)

        os.chdir(dir)
        os.system(os.environ["SHELL"])
        return

    click.echo(ctx.get_help())