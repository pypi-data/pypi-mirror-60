from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError

from check_ip.config import ConfigError


class CloudFlareAPIClientError(Exception):
    """Raised when the client cannot fulfill a request."""


class CloudflareAPIClient:
    def __init__(self, email, api_key):
        self.client = CloudFlare(email=email, token=api_key)
        self._validate_auth()

    def _validate_auth(self):
        try:
            self.client.user.get()
        except CloudFlareAPIError as err:
            raise ConfigError(
                "Authentication information incorrect, please check your configuration file."
            ) from err

    def get_dns_record(self, zone_name, record_name):
        """Get a DNS record in a given zone."""
        all_dns_records = self._get_dns_records(zone_name)
        if record_name not in all_dns_records:
            raise CloudFlareAPIClientError(
                f"Could not find a DNS record with name '{record_name}'."
            )
        return all_dns_records[record_name]

    def update_dns_record(self, zone_name, record_name, new_content):
        """Update a DNS record in a given zone with the given name.

        Assumes an "A" record.
        """
        zone = self._get_zone(zone_name)
        record = self.get_dns_record(zone_name, record_name)

        return self.client.zones.dns_records.put(
            zone["id"],
            record["id"],
            data={"name": record_name, "type": "A", "content": new_content},
        )

    def _get_zone(self, zone_name):
        """Get a zone by name."""
        zones = self.client.zones.get(params={"name": zone_name})
        if not zones:
            raise CloudFlareAPIClientError(
                f"Could not find zone with name '{zone_name}'."
            )
        return zones[0]

    def _get_dns_records(self, zone_name):
        """Get DNS records in a given zone.

        Only get "A" records.
        """
        zone = self._get_zone(zone_name)

        all_dns_records = self.client.zones.dns_records.get(zone["id"])
        return {
            record["name"]: record
            for record in all_dns_records
            if record["type"] == "A"  # Only need to look at A records.
        }
