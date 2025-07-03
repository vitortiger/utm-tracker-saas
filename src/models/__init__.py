from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from src.models.user import User
from src.models.telegram_bot import TelegramBot
from src.models.campaign import Campaign
from src.models.lead import TelegramLead
from src.models.invite_link import InviteLink
