from crisprbact import on_target_predict
from Bio import SeqIO
import click


class Config(object):
    def __init__(self):
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)

HEADER = ["target", "PAM position", "prediction", "seq_id"]


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@pass_config
def main(config, verbose):
    config.verbose = verbose


@main.group()
@pass_config
def predict(config):
    pass


@predict.command()
@click.option("-t", "--target", type=str, required=True)
@click.argument("output-file", type=click.File("w"), default="-")
@pass_config
def from_str(config, target, output_file):
    """
    Outputs candidate guide RNAs for the S. pyogenes dCas9 with predicted on-target
    activity from a target gene.

    [OUTPUT_FILE] file where the candidate guide RNAs are saved. Default = "stdout"

    """
    if config.verbose:
        print_parameters(target)

    guide_rnas = on_target_predict(target)
    click.echo("\t".join(HEADER), file=output_file)
    write_guide_rnas(guide_rnas, output_file)


@predict.command()
@click.option(
    "-t", "--target", type=click.File("rU"), required=True, help="Sequence file"
)
@click.option(
    "-f",
    "--seq-format",
    type=click.Choice(["fasta", "fa", "gb", "genbank"]),
    help="Sequence file format",
    default="fasta",
    show_default=True,
)
@click.argument("output-file", type=click.File("w"), default="-")
@pass_config
def from_seq(config, target, seq_format, output_file):
    """
    Outputs candidate guide RNAs for the S. pyogenes dCas9 with predicted on-target
    activity from a target gene.

    [OUTPUT_FILE] file where the candidate guide RNAs are saved. Default = "stdout"

    """
    fg = "blue"
    if config.verbose:
        print_parameters(target.name, fg)
    click.echo("\t".join(HEADER), file=output_file)
    for record in SeqIO.parse(target, seq_format):
        if config.verbose:
            click.secho(" - search guide RNAs for %s " % record.id, fg=fg)
        guide_rnas = on_target_predict(str(record.seq))
        write_guide_rnas(guide_rnas, output_file, record.id)


def print_parameters(target, fg="blue"):
    click.secho("[Verbose mode]", fg=fg)
    click.secho("Target sequence : %s" % target, fg=fg)


def write_guide_rnas(guide_rnas, output_file, seq_id="N/A"):

    for guide_rna in guide_rnas:
        # click.echo(guide_rna)
        click.echo(
            "\t".join(
                [
                    guide_rna["target"],
                    str(guide_rna["pam"]),
                    str(guide_rna["pred"]),
                    seq_id,
                ]
            ),
            file=output_file,
        )


if __name__ == "__main__":
    main()
