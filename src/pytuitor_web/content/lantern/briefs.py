"""Authored milestone briefs shared by teaching, the overview, and achievements."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MilestoneBrief:
    existing: str
    addition: str
    preserve: str
    example: str
    outcome: str

    def markdown(self) -> str:
        return (
            "## Your implementation brief\n\n"
            f"**Already working:** {self.existing}\n\n"
            f"**Add now:** {self.addition}\n\n"
            f"**Keep working:** {self.preserve}\n\n"
            f"**Try it:**\n\n```text\n{self.example}\n```\n"
        )


BRIEFS = {
    "arrival": MilestoneBrief(
        "This is the first scene; start with an empty game.py.",
        "Ask four questions, calculate supply days, and choose a safe route.",
        "Use the specified final four lines; your prompt wording can be personal.",
        "Explorer name: Ada\nFood packs: 2\nTrail distance: 2.5\nRoute: ridge\nTake the ridge.",
        "Your game welcomes an explorer and chooses a route from their supplies.",
    ),
    "pack": MilestoneBrief(
        "The arrival scene asks questions and chooses a route.",
        "Describe an ordered pack and identify the equipment you still need.",
        "Keep the arrival scene and repeated supplies in their original order.",
        "Your pack:\nrope\nfood\nfood\nPacked items: 3\nUnique supplies: 2\nLamp missing: True",
        "Your explorer has a pack with ordered supplies and an equipment check.",
    ),
    "outpost": MilestoneBrief(
        "You can describe supplies and a chosen route.",
        "Replace the one-time questionnaire with a repeatable command loop.",
        "Keep locations and supplies consistent; unknown commands must leave them alone.",
        "> forest\n> gather\n> inventory\n> quit",
        "Your explorer can travel, gather supplies, and keep playing until they choose to stop.",
    ),
    "quests": MilestoneBrief(
        "The command loop explores the valley and updates supplies.",
        "Extract new_game, describe, step, and main; help Mira with a delivery.",
        "Keep existing commands, independent game states, and valid supplies after bad input.",
        "> forest\n> gather\n> gather\n> outpost\n> deliver\nMira repairs the beacon frame.",
        "Your game has a resident quest and reusable rules for every command.",
    ),
    "saves": MilestoneBrief(
        "An expedition can travel, gather, eat, and complete a delivery.",
        "Save and load JSON state and exchange a CSV supply ledger.",
        "Failed loading must leave the active expedition intact; retain existing commands.",
        "> save\n> load\n> inventory",
        "Your game can save an expedition and restore it on a later run.",
    ),
    "markers": MilestoneBrief(
        "Game state and supply ledgers can be saved.",
        "Validate, extract, and rewrite trail marker codes using text patterns.",
        "Keep unrelated text untouched and reject incomplete or embedded invalid codes.",
        "> decode Follow FR-012 to the ridge.",
        "Your game can read coded trail markers without damaging the surrounding note.",
    ),
    "modules": MilestoneBrief(
        "The single-file game includes quests, saves, and trail markers.",
        "Move rules into engine.py; keep game.py as the public launcher and check interface.",
        "Imports stay quiet; preserve commands and expose the documented functions from game.py.",
        "python game.py --name Ada --seed 7\n> scout\n> summary",
        "Your game has reusable modules, player options, and repeatable scouting.",
    ),
    "calendar": MilestoneBrief(
        "The modular expedition has a repeatable command interface.",
        "Calculate in-game dates and delivery deadlines with explicit inputs.",
        "Keep prior features and use game dates rather than the computer clock.",
        "> calendar",
        "Your expedition can plan supply runs across calendar boundaries.",
    ),
    "depot": MilestoneBrief(
        "Supplies, residents, and the game calendar are available.",
        "Group deliveries, process requests in order, and help Oren and Tess.",
        "Do not change callers' collections; retain Mira's quest and all existing commands.",
        "> help oren\n> depot\n> help tess",
        "Your settlement can serve residents and build a storehouse.",
    ),
    "classes": MilestoneBrief(
        "The outpost has supplies, quests, and scheduled work.",
        "Give Expedition instances their own state and write tests for important transitions.",
        "Keep the functional interface for earlier checks; each expedition owns its nested state.",
        "python -m unittest\n> inventory\n> deliver",
        "Your game has a tested expedition object with independent state.",
    ),
    "beacon": MilestoneBrief(
        "The expedition engine has tested quests and persistent state.",
        "Restore the beacon and add careful, previewable journal archives.",
        "Validate paths before writing and never overwrite an existing archive.",
        "> forest\n> gather\n> gather\n> outpost\n> deliver\n> beacon\n"
        "The beacon shines. Lantern Reach is home again.",
        "Your core adventure is complete: the beacon shines over a working outpost.",
    ),
    "branches": MilestoneBrief(
        "The core adventure is playable through its ending.",
        "Make independent branches of nested state and preserve valid zero or empty choices.",
        "Trying a route must not alter the original expedition or its inventory.",
        "> branch",
        "Your explorer can try another route without losing the original state.",
    ),
    "caves": MilestoneBrief(
        "You can branch an expedition without sharing mutable state.",
        "Traverse nested cave routes and accept a callable ordering strategy.",
        "Retain route order, empty branches, and all inherited optional features.",
        "> caves\nentrance, pool, crystal chamber",
        "Your game can explore a nested cave network.",
    ),
    "actions": MilestoneBrief(
        "Core commands work and independent branches are available.",
        "Record successful actions with configurable wrappers.",
        "Keep arguments, return values, callable metadata, and inherited features.",
        "> actions",
        "Your expedition can record actions through reusable decorators.",
    ),
    "chronicle": MilestoneBrief(
        "Core commands and independent branches are available.",
        "Read matching chronicle events lazily and stop at the requested limit.",
        "Do not consume more source events than needed; keep carried optional features.",
        "> chronicle",
        "Your game can read a chronicle without loading its entire event stream.",
    ),
    "stations": MilestoneBrief(
        "Actions can be wrapped and event streams can be consumed carefully.",
        "Manage temporary field-station visits and report useful domain failures.",
        "Restore prior state on success and failure, including nested visits.",
        "> station",
        "Your explorer can visit a field station and reliably recover their previous state.",
    ),
    "records": MilestoneBrief(
        "The core game can branch independent expedition state.",
        "Create typed field records with validated values and independent notes.",
        "Defaults must not share mutable data; validate updated records too.",
        "> records",
        "Your expedition has validated field records with independent notes.",
    ),
    "stores": MilestoneBrief(
        "Validated field records are available.",
        "Define a small supply-store contract and test reports through an injected writer.",
        "Accept equivalent store implementations and retain every carried game feature.",
        "> stores",
        "Your game can work with interchangeable supply stores.",
    ),
    "scouts": MilestoneBrief(
        "The expedition can manage station lifetimes and failures.",
        "Coordinate offline scout tasks with a concurrency limit and owned cancellation.",
        "Preserve input order and wait for cleanup before a cancelled operation finishes.",
        "> scouts",
        "Your game can coordinate scout teams and clean up cancelled work.",
    ),
    "package": MilestoneBrief(
        "A complete core adventure works; other extensions may also be present.",
        "Move owned modules into lantern_reach/ and add a CLI and package metadata.",
        "Root launchers keep earlier checks working; package imports "
        "stay quiet and self-contained.",
        "python -m lantern_reach --name Ada\n> help",
        "Your game can be installed and launched as an independent Python package.",
    ),
    "formatters": MilestoneBrief(
        "The game has field records and a supply-store interface.",
        "Register, inspect, and safely extend journal formatters.",
        "Keep descriptor state per instance, reject duplicate "
        "registrations, and retain prior commands.",
        "> formatters\nTrail: The beacon shines.",
        "Your game supports discoverable journal formatter extensions.",
    ),
    "ranger": MilestoneBrief(
        "The core adventure is complete and the beacon can be lit.",
        "Send an expedition report to a ranger station's web API, with pytest tests and "
        "listed requirements.",
        "Keep every command playable offline; a missing station gives a calm message, "
        "never a crash.",
        "> report http://127.0.0.1:8000\nReport filed: #12",
        "Your game can report to a ranger station and proves it with offline pytest tests.",
    ),
}
