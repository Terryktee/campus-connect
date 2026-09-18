"use client";

import { FormEvent, useState } from "react";
import { ApiError, follow, unfollow, type FollowTarget } from "@/lib/api";

const CONTACT_KEY = "campusconnect-follower-contact";

function rememberedContact() {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(CONTACT_KEY) || "";
}

export function FollowButton({
  target,
  label = "Follow",
}: {
  target: FollowTarget;
  label?: string;
}) {
  const [contact, setContact] = useState("");
  const [draft, setDraft] = useState("");
  const [needsContact, setNeedsContact] = useState(false);
  const [state, setState] = useState<
    "idle" | "following" | "followed" | "already" | "unfollowing" | "error"
  >("idle");
  const [error, setError] = useState("");

  const submit = async (event?: FormEvent) => {
    event?.preventDefault();
    const nextContact = contact || draft.trim() || rememberedContact();
    if (!nextContact) {
      setNeedsContact(true);
      return;
    }
    setError("");
    setState("following");
    try {
      await follow(nextContact, target);
      window.localStorage.setItem(CONTACT_KEY, nextContact);
      setContact(nextContact);
      setDraft("");
      setNeedsContact(false);
      setState("followed");
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409) {
        window.localStorage.setItem(CONTACT_KEY, nextContact);
        setContact(nextContact);
        setDraft("");
        setNeedsContact(false);
        setState("already");
      } else {
        setState("error");
        setError(
          reason instanceof ApiError
            ? reason.message
            : "We could not save your follow.",
        );
      }
    }
  };

  const remove = async () => {
    const nextContact = contact || rememberedContact();
    if (!nextContact) {
      setNeedsContact(true);
      return;
    }
    setError("");
    setState("unfollowing");
    try {
      await unfollow(nextContact, target);
      setState("idle");
    } catch (reason) {
      setState("error");
      setError(
        reason instanceof ApiError
          ? reason.message
          : "We could not remove your follow.",
      );
    }
  };

  if (needsContact) {
    return (
      <form className="follow-form" onSubmit={submit}>
        <label htmlFor="follower-contact">Email or phone</label>
        <div className="follow-form-row">
          <input
            id="follower-contact"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="you@example.com or 077..."
            required
          />
          <button className="button primary" type="submit">
            Save &amp; follow
          </button>
        </div>
        <small>We use this only to send updates about what you follow.</small>
      </form>
    );
  }

  if (state === "followed" || state === "already" || state === "unfollowing") {
    return (
      <div className="follow-status">
        <span role="status">
          {state === "already" ? "Already following" : "Following"}
        </span>
        <button
          className="button ghost"
          onClick={remove}
          disabled={state === "unfollowing"}
        >
          {state === "unfollowing" ? "Removing…" : "Unfollow"}
        </button>
      </div>
    );
  }

  return (
    <div className="follow-control">
      <button
        className="button ghost"
        onClick={() => submit()}
        disabled={state === "following"}
      >
        {state === "following" ? "Following…" : label}
      </button>
      {state === "error" && (
        <small className="form-error" role="alert">
          {error}
        </small>
      )}
    </div>
  );
}
