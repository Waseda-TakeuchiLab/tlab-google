# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
import base64
import dataclasses
from email.mime import base as mimebase
import typing as t

from tlab_google import abstract


Message = dict[str, t.Any]


@dataclasses.dataclass()
class GmailAPI(abstract.AbstractAPI):
    """Gmail API wrapper.

    Examples
    --------
    ### Create a GmailAPI object
    >>> from tlab_google import Credentials, GmailAPI
    >>> from email.mime import text
    >>> creds = Credentials.from_file("credentials.json")
    >>> api = GmailAPI(creds)

    ### Send a message
    Create a message.
    >>> to = "foobar@example.com"  # Replace it with your email address
    >>> subject = "API Test"
    >>> body = "This is a test mail of Gmail API."
    >>> message = text.MIMEText(body)
    >>> message["to"] = to
    >>> message["subject"] = subject

    Send a message.
    >>> api.send_email(message)

    ### Search messages and Get a message.
    >>> query = "subject:(Laboratory)"
    Search messages in Gmail box.
    >>> results, next_page_token, size = api.search_email(query)

    Get a message.
    >>> msg_id = results[0]["id"]
    >>> gmail = api.get_email(msg_id)

    Get the subject of the message.
    >>> headers = {header["name"]: header["value"] for header in gmail["payload"]["headers"]}
    >>> subject = headers["Subject"]
    """
    user_id: str = "me"
    """The user's email address."""

    def __post_init__(self) -> None:
        super().__init__(self.credentials, self.version or "v1")

    @property
    def service_name(self) -> str:
        return "gmail"

    @property
    def _service(self) -> t.Any:
        return abstract.build_service(self)

    def search_email(
        self,
        query: str,
        max_results: int = 100,
        page_token: str | None = None,
        label_ids: list[str] | None = None,
        include_spam_trash: bool = False
    ) -> tuple[list[Message], str, int]:
        """Search the user's mailbox on Gmail.

        Parameters
        ----------
        query : str
            The same query format as that of the Gmail search box.
        max_results : int
            Maximum number of messages to return.
        page_token : str | None
            An page token to retrieve a specific page of results in the list.
        label_ids : list[str] | None
            List of label IDs of messages to retrieve.
        include_spam_trash : bool
            If true, messages from SPAM and TRASH are included in the results.

        Returns
        -------
        messages : list[tlab_google.gmail.Message]
            List of messages.
            See also https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message for Message.
        next_page_token : str
            An token to retrieve the next page.
        result_size_estimate : int
            Estimated total number of results.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
        """
        result = self._service.users().messages().list(
            userId=self.user_id,
            q=query,
            maxResults=max_results,
            pageToken=page_token or "",
            labelIds=label_ids or [],
            includeSpamTrash=include_spam_trash
        ).execute()
        messages = [
            {str(key): message[key] for key in message}
            for message in result.get("messages", [])
        ]
        next_page_token = str(result.get("nextPageToken", ""))
        result_size_estimate = int(result.get("resultSizeEstimate", 0))
        return messages, next_page_token, result_size_estimate

    def get_email(
        self,
        id: str,
        format: t.Literal["minimal", "full", "raw", "metadata"] = "full"
    ) -> Message:
        """Get a email in the mailbox of Gmail.

        Parameters
        ----------
        id : str
            An ID of the message to retrieve.
        format : Literal["minimal", "full", "raw", "metadata"]
            The format to return the message in.
            See also https://developers.google.com/gmail/api/reference/rest/v1/Format.

        Returns
        -------
        tlab_google.gmail.Message
            See also https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message for Message.

        See Also
        --------
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get
        """
        result = self._service.users().messages().get(
            userId=self.user_id,
            id=id,
            format=format
        ).execute()
        return {str(key): result[key] for key in result}

    def send_email(self, message: mimebase.MIMEBase) -> None:
        """Send a email via Gmail.

        Parameters
        ----------
        message : email.mime.base.MIMEBase
            A message to send.
        """
        raw_body = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self._service.users().messages().send(
            userId=self.user_id,
            body={"raw": raw_body}
        ).execute()

    def get_signature(self, address: str | None = None) -> str:
        """Get a signature registered on Gmail.

        Parameters
        ----------
        address : str | None
            A send-as alias to be retrieved.
            If None, the default send-as alias is retrieved.

        Returns
        -------
        str
            A HTML text of signature of the address.

        Raises
        ------
        ValueError
            If a signature for the address is not found.
        """
        response = self._service.users().settings().sendAs().list(
            userId=self.user_id,
        ).execute()
        addr_to_sendas = {
            sendas["sendAsEmail"]: sendas for sendas in response.get("sendAs", [])
        }
        if address is None:
            # Get the default send-as alias
            sendas = [sendas for sendas in addr_to_sendas.values() if sendas.get("isDefault", False)].pop()
        else:
            if address not in addr_to_sendas.keys():
                raise ValueError(f"A signature for {address} not found")
            sendas = addr_to_sendas[address]
        return str(sendas.get("signature", ""))
