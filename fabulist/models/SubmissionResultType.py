from enum import Enum


class SubmissionResultType(Enum):
    """The SubmissionResultType class represents the possible results or status of a story submission.

    Attributes
    ----------
        ACCEPTED: str
            The submission was accepted
        REJECTED: str
            The submission was rejected
        REWRITE_REQUESTED: str
            The submission was requested to be rewritten
        PENDING: str
            The submission is pending
        WITHDRAWN: str
            The submission was withdrawn
        IGNORED: str
            The submission was ignored
    """

    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    REWRITE_REQUESTED = 'Rewrite Requested'
    PENDING = 'Pending'
    WITHDRAWN = 'Withdrawn'
    IGNORED = 'Ignored'
