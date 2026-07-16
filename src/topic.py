import random

TOPICS = [
    "Mondays",
    "coffee addiction",
    "procrastination",
    "the gym",
    "cooking fails",
    "working from home",
    "group chats",
    "existential dread",
    "cats vs dogs",
    "budgeting",
    "social media addiction",
    "video games",
    "adulting",
    "traffic",
    "diets",
    "sleep schedules",
    "online shopping",
    "small talk",
    "weather",
    "wifi issues",
    "Monday meetings",
    "self care",
    "productivity hacks",
    "AI taking over",
    "streaming service overload",
    "email inboxes",
    "parallel parking",
    "IKEA furniture",
    "houseplants",
    "public transport",
    "leftovers",
]


def random_topic() -> str:
    return random.choice(TOPICS)
