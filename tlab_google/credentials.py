# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import os
import dataclasses

from google.auth.transport import requests
from google.oauth2 import credentials
from google_auth_oauthlib import flow


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]
CLIENT_CONFIG = {
    "installed": {
        "client_id": "629905107772-2rq0b441g8k6v428ul0hvhlp0p8pq09a.apps.googleusercontent.com",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
    }
}


@dataclasses.dataclass()
class Credentials:
    """Oauth 2.0 credentials for Google API.

    Examples
    --------
    >>> from tlab_google import Credentials

    Get a new Credentials.
    >>> creds = Credentials.new()

    Save the Credentials.
    >>> creds_file = "credentials.json"
    >>> creds.save(creds_file)

    Get a Credentials from file.
    >>> creds = Credentials.from_file(creds_file)

    Refresh the Crendentials.
    >>> creds.reflesh()
    """
    _credentials: credentials.Credentials
    """Actual credentials."""

    @classmethod
    def new(
        cls,
        scopes: list[str] | None = None,
        client_id: str = "",
        client_secret: str = "",
        run_local_server: bool = True
    ) -> "Credentials":
        """Create a new Credentials instance for Google API.

        Parameters
        ----------
        scopes : list[str] | None
            List of scopes to request during the flow.
        client_id : str
            The client ID of the GCP project.
        client_secret : str
            The client secret of the GCP project.
        run_local_server : bool
            If true, a local server runs for the authorization flow.
            Otherwise, the user manually enters the authorization code instead.

        Returns
        -------
        tlab_google.credentials.Credentials
            A new OAuth 2.0 credentials.
        """
        client_config = CLIENT_CONFIG.copy()
        if client_id:
            client_config["installed"]["client_id"] = client_id
        if client_secret:
            client_config["installed"]["client_secret"] = client_secret
        _flow = flow.InstalledAppFlow.from_client_config(client_config, scopes or SCOPES)
        creds = _flow.run_local_server() if run_local_server else _flow.run_console()
        return cls(creds)

    @classmethod
    def from_file(
        cls,
        filename: str | os.PathLike[str],
        scopes: list[str] | None = None
    ) -> "Credentials":
        """Create a Credentials instance for Google API from an authorized user json file.

        Parameters
        ----------
        filename : str | os.PathLike[str]
            The path to the authorized user json file.
        scopes : list[str] | None
            List of scopes to request during the flow.

        Returns
        -------
        tlab_google.credentials.Credentials
            The constructed OAuth 2.0 credentials.

        Raises
        ------
        ValueError
            If the constructed credentials is invalid.
        """
        creds = credentials.Credentials.from_authorized_user_file(filename, scopes or SCOPES)
        if not creds.valid:
            if creds.refresh_token:
                creds.refresh(requests.Request())
            else:
                raise ValueError("The credentials is not valid and has no refresh token")
        return cls(creds)

    def save(self, filename: str | os.PathLike[str]) -> None:
        """Save a Credentials instance as a json file.

        Parameters
        ----------
        filename : str | os.PathLike[str]
            The path to save the credentials.
        """
        with open(filename, "w") as f:
            f.write(self._credentials.to_json())

    def refresh(self) -> None:
        """Refresh the access token."""
        self._credentials.refresh(requests.Request())
