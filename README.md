# 🔮 RicksVision
Know the perfect time to hop in the Rick's line using AI.

In collaboration with [ricksline.bar](https://ricksline.bar) 🥂


## Getting started
We use `uv` as our Python package manager and `git-lfs` to manage large videos.

Make sure you have both installed (assuming macOS):
```
brew install uv
brew install git-lfs
```

Then, setup and start the frontend dev server:

```
cd client
pnpm install
pnpm dev
```

Finally, setup and start the FastAPI server:
```
cd server
uv run fastapi dev
```
