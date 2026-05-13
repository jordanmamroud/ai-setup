# tuning

Growing corpus of agent responses I save to refine how I instruct agents across
my projects.

## Layout

```
tuning/
├── README.md
├── good-responses.md     ← prompt+good-response entries (appended by savegood)
└── bad-responses.md      ← prompt+bad-response entries (appended by savebad)
```

The shell scripts `savegood` and `savebad` themselves live in
`~/mylab/ai-setup/terminal/shortcuts/` (where all global shortcuts live).
They write into the corpus files here.

## How I use the corpus

When an agent gives a response I like or don't like, I run `savegood` /
`savebad` from the project folder I was working in. Each entry gets a
timestamp and a `**Source:**` line auto-filled with the current directory,
so I can see which project's context produced it.

Over time, I look for patterns in what makes responses good or bad and roll
the lessons into my global `CLAUDE.md` (or project-level instructions). The
corpus is the raw material for tuning agent behavior.
