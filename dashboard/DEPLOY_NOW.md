# 🚀 DEPLOY IN 3 COMMANDS

## Fastest Deployment Path

```bash
cd "/Users/Johan/Documents/Coding AI/horizon-gaming-detector/dashboard"
vercel login
vercel --prod
```

That's it! Your dashboard will be live in 2-3 minutes.

---

## Alternative: One-Click Script

```bash
cd "/Users/johan/Documents/Coding AI/horizon-gaming-detector/dashboard"
./deploy.sh
```

---

## What Happens During Deployment

1. **Build** (30 seconds): Compiles Next.js app with optimizations
2. **Upload** (30 seconds): Transfers build files to Vercel CDN
3. **Deploy** (60 seconds): Makes site live on global edge network

**Total Time**: ~2-3 minutes

---

## After Deployment

Your dashboard will be live at:
```
https://[project-name].vercel.app
```

Test these features:
- [ ] Homepage loads
- [ ] 4 metric cards display
- [ ] Charts render (time series, breakdowns, pie)
- [ ] Filters work (date, provider, country, method)
- [ ] Anomaly table is sortable and filterable
- [ ] Responsive on mobile/tablet

---

## Troubleshooting

**"Token not valid" error?**
→ Run `vercel login` first

**Build fails?**
→ Run `npm run build` locally to test

**404 on deployment?**
→ Check root directory is set to `dashboard` in Vercel settings

---

## Need Help?

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
