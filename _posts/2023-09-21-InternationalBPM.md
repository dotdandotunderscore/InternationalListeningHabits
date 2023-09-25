---
title: Variation in average BPM of pop songs in different countries
date: 2023-09-20 14:05:00 -500
categories: [Spotify, BPM]
tags: [data, visualisation]
---

## Music is complicated

Comparing pieces of music from a scientific perspective has gained major traction with the popularity of Spotify and its powerful song suggestion algorithm.

The Spotify API contains a wide variety of aggregated audio feature endpoints that let us get a glimpse into the data that Spotify's algorithm uses for suggestions.

In the first part of this project the tempo, or beats per minute, of the top 50 songs in each country that Spotify keeps a "Top 50" playlist for are exposed. The plot is interactive, hover over data points to see song names and BPMs! The blue line shows the averaged BPM across all 50 songs, which lets us see some interesting international trends: Why do Denmark and Italy prefer lower BPMs than so many other countries?

(If viewing on mobile, make sure to switch to landscape mode)

<iframe src="../../code/BPMVis/BPM.html" width="100%" height="600" allowtransparency="true" frameborder="0"></iframe>