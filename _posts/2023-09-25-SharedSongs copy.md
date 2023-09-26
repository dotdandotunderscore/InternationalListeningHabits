---
title: Aggregating data on Top 50 similarities
date: 2023-09-25 09:40:00 -500
categories: [Spotify, Cultural Groups]
tags: [data, visualisation]
---

## Simplifying data exposes its value

The previous post on this site used the Spotify API to produce a series of plots that contained data on how many songs are shared between the Top 50 playlists officially maintained by Spotify. The 30 plots in total presented an explicit and complete view of that data set, but in a way which was quite difficult to consume, especially on mobile. By instead plotting the data as a mirrored matrix (suggested by a friend), all of that data can be shown on a single plot. Some of the relationships and behaviours are a bit less clear to see, but I feel that what is lost is made up for by being able to see everything in one plot. The previous post is still available [here](https://dotdandotunderscore.github.io/posts/SharedSongs/) if you would like to see everything.

Also included here is a plot showing the average number of shared songs across all Top 50 lists. This illuminates the reach of each country not just in their popularity in other countries, but also in their exposure to external music. We again see the isolation of the Spanish speaking nations and the high related-ness of countries in Oceania.

(If viewing on mobile, make sure to switch to landscape mode)

<iframe src="../../code/SharedSongs/SharedHeatmap.html" width="100%" height="600"></iframe>
<iframe src="../../code/SharedSongs/SharedHist.html" width="100%" height="600"></iframe>
