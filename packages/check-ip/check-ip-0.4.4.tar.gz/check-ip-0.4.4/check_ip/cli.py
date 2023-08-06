import click
from requests import RequestException

from check_ip.api import get_public_ip
from check_ip.api.cloudflare import CloudflareAPIClient
from check_ip.api.cloudflare import CloudFlareAPIClientError
from check_ip.config import Config
from check_ip.config import ConfigError


@click.command()
@click.argument("config_file")
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def main(ctx, config_file, verbose):
    """Check your public IP address and update DNS records on Cloudflare."""
    # Load config.
    try:
        config = Config.from_file(config_file)
        config.verbose = verbose
        cloudflare_api_client = CloudflareAPIClient(config.email, config.api_key)

        # Get the current public IP.
        public_ip = get_public_ip()

        # For each record name in the config, check the content and update if necessary.
        for record_name in config.record_names:
            record = cloudflare_api_client.get_dns_record(config.zone, record_name)

            if record["content"] == public_ip:
                if verbose:
                    click.echo(
                        f"Public IP matches {record_name} ({record['content']})",
                        err=True,
                    )
                continue
            click.echo(
                f"Public IP ({public_ip}) does not match {record_name} ({record['content']})",
                err=True,
            )

            # Update the record IP address.
            cloudflare_api_client.update_dns_record(config.zone, record_name, public_ip)
            click.echo(
                f"Updated record for {record['name']}: {record['content']} -> {public_ip}",
                err=True,
            )
    except (ConfigError, RequestException, CloudFlareAPIClientError) as err:
        ctx.fail(err)
