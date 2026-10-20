import { useEffect, useState } from "react";
import {
  ArrowRight,
  Check,
  Compass,
  Download,
  History,
  Mountain,
  Play,
  RotateCcw,
  Sprout,
} from "lucide-react";
import { api, download } from "../api";
import { useApp } from "../context";
import { PlayDialog } from "../components/extras";
import { Spinner, TopBarSlot, formatBytes } from "../components/ui";
import { learnPath, navigate } from "../router";
import type { Game as GameData } from "../types";

export function Game() {
  const { fail, confirm, toast, refresh } = useApp();
  const [game, setGame] = useState<GameData | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [playing, setPlaying] = useState<{ id: string; title: string } | null>(null);

  useEffect(() => {
    api<GameData>("/game")
      .then((data) => {
        setGame(data);
        setSelected(
          data.last_milestone ??
            data.milestones.find((item) => item.status !== "completed")?.id ??
            data.milestones[0].id,
        );
      })
      .catch(fail);
  }, [fail]);

  if (!game) {
    return (
      <div className="page-loading">
        <Spinner size={22} />
      </div>
    );
  }
  const milestone = game.milestones.find((item) => item.id === selected) ?? game.milestones[0];
  const done = game.milestones.filter((item) => item.status === "completed").length;
  const versions = game.checkpoints.filter((item) => item.milestone === milestone.id);
  const totalBytes = game.checkpoints.reduce((sum, item) => sum + item.bytes, 0);

  const chooseBase = async (checkpoint?: string) => {
    const proceed = await confirm({
      title: checkpoint
        ? "Restore this version into a new draft?"
        : "Start from supplied earlier code?",
      body: checkpoint
        ? `Both current drafts for ${milestone.title} are backed up first. The restored copy must pass its checks again.`
        : "This is the working game before this milestone, not its solution. Earlier milestones stay incomplete." +
          (milestone.started ? " Both current drafts are backed up first." : ""),
      confirm: checkpoint ? "Back up and restore" : "Use supplied base",
      danger: milestone.started,
    });
    if (!proceed) return;
    try {
      const result = await api<{ backup: string | null; game: GameData }>(
        `/game/${milestone.id}/base`,
        { checkpoint: checkpoint ?? null },
      );
      setGame(result.game);
      void refresh();
      toast(
        result.backup ? `Ready. Previous drafts backed up to ${result.backup}` : "Ready to open.",
        "success",
      );
    } catch (error) {
      fail(error);
    }
  };

  return (
    <div className="page game">
      <TopBarSlot>
        <nav className="crumbs">
          <span className="current">Your game</span>
        </nav>
      </TopBarSlot>
      <header className="game-hero">
        <div className="game-hero-art" aria-hidden="true">
          <Mountain size={120} strokeWidth={0.8} />
        </div>
        <p className="eyebrow">
          <Compass size={13} /> Your growing game
        </p>
        <h1>{game.title}</h1>
        <p className="lede">{game.description}</p>
        <div className="game-stats">
          <span>
            <strong>{done}</strong> of {game.milestones.length} milestones
          </span>
          <span>
            <strong>{game.checkpoints.length}</strong> working{" "}
            {game.checkpoints.length === 1 ? "version" : "versions"}
          </span>
          <span>
            <strong>{formatBytes(totalBytes)}</strong> of history
          </span>
          {game.checkpoints.length > 0 && (
            <button
              className="btn sm"
              onClick={() => download(`/game/checkpoints/${game.checkpoints[0].id}/export`)}
            >
              <Download size={14} /> Download latest game
            </button>
          )}
        </div>
      </header>

      <div className="game-layout">
        <ol className="trail" aria-label="Milestones">
          {game.milestones.map((item) => (
            <li key={item.id}>
              <button
                className={`trail-stop ${item.status.replace(" ", "-")} ${item.id === milestone.id ? "on" : ""}`}
                onClick={() => setSelected(item.id)}
                aria-current={item.id === milestone.id}
              >
                <span className="trail-node">
                  {item.status === "completed" ? <Check size={13} strokeWidth={3} /> : item.number}
                </span>
                <span className="trail-text">
                  <strong>{item.title}</strong>
                  {item.optional && <span className="badge">Optional</span>}
                </span>
              </button>
            </li>
          ))}
        </ol>

        <section className="milestone-detail card">
          <p className="eyebrow">
            Milestone {milestone.number} · {milestone.minutes} min · Extend + Repair
          </p>
          <h2>{milestone.title}</h2>
          <p className="milestone-outcome">{milestone.outcome}</p>
          <p className="callout game">
            <Sprout size={16} />
            <span>{milestone.origin}</span>
          </p>
          <div className="row">
            <button className="btn primary" onClick={() => navigate(learnPath(milestone.id))}>
              {milestone.started ? "Continue milestone" : "Open milestone"} <ArrowRight size={15} />
            </button>
            {milestone.supplied_base && (
              <button className="btn" onClick={() => void chooseBase()}>
                <RotateCcw size={14} /> Start from supplied code
              </button>
            )}
          </div>
          <p className="muted small">
            Preparation is advisory. Working versions are kept until you explicitly start over.
          </p>

          <h3 className="section-title">
            <History size={15} /> Working versions of this milestone
          </h3>
          {versions.length ? (
            <ul className="versions">
              {versions.map((item) => (
                <li key={item.id}>
                  <div>
                    <strong>{new Date(item.created).toLocaleString()}</strong>
                    <span className="muted small">
                      {item.supported ? "Used supplied code or a reference" : "Your own code"} ·{" "}
                      {formatBytes(item.bytes)} · <code>{item.id.slice(0, 10)}</code>
                    </span>
                  </div>
                  <div className="row">
                    <button
                      className="btn sm"
                      onClick={() => setPlaying({ id: item.id, title: item.title })}
                    >
                      <Play size={13} /> Play
                    </button>
                    <button
                      className="icon-btn"
                      aria-label="Download this version"
                      title="Download (.zip)"
                      onClick={() => download(`/game/checkpoints/${item.id}/export`)}
                    >
                      <Download size={14} />
                    </button>
                    <button
                      className="icon-btn"
                      aria-label="Restore this version"
                      title="Restore into a new draft"
                      onClick={() => void chooseBase(item.id)}
                    >
                      <RotateCcw size={14} />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">
              Pass the Extend checks to save this milestone's first working version.
            </p>
          )}
          {game.checkpoints.length > versions.length && (
            <>
              <h3 className="section-title">Earlier versions</h3>
              <ul className="versions compact">
                {game.checkpoints
                  .filter((item) => item.milestone !== milestone.id)
                  .slice(0, 6)
                  .map((item) => (
                    <li key={item.id}>
                      <div>
                        <strong>{item.title}</strong>
                        <span className="muted small">
                          {new Date(item.created).toLocaleDateString()}
                        </span>
                      </div>
                      <button
                        className="btn sm"
                        onClick={() => setPlaying({ id: item.id, title: item.title })}
                      >
                        <Play size={13} /> Play
                      </button>
                    </li>
                  ))}
              </ul>
            </>
          )}
        </section>
      </div>
      {playing && (
        <PlayDialog
          checkpoint={playing.id}
          title={playing.title}
          onClose={() => setPlaying(null)}
        />
      )}
    </div>
  );
}
