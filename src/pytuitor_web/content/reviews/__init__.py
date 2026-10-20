"""Optional authored mixed reviews, one session per syllabus chapter."""

from pytuitor_web.content.reviews.core import CORE
from pytuitor_web.content.reviews.depth import DEPTH
from pytuitor_web.content.reviews.online import ONLINE

REVIEWS = CORE | DEPTH | ONLINE
