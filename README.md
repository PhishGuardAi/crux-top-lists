# Chrome (CrUX) Top Lists

[Recent research](https://zakird.com/papers/toplists.pdf) has shown that the Chrome User Experience Report (CrUX) data published by Google Chrome via their [UX Report](https://developer.chrome.com/docs/crux/) is significantly more accurate than other top lists like the Alexa Top Million and Tranco Top Million for capturing the most popular websites on the Internet.

This repository caches a CSV version of the Chrome websites list, queried from the public CrUX data in Google BigQuery. You can browse all of the cached lists [here](https://github.com/zakird/crux-top-lists/tree/main/data/global).

The most up-to-date global websites list can be downloaded directly at:
https://raw.githubusercontent.com/PhishGuardAi/crux-top-lists/main/data/global/current.csv.gz.

### Data Structure

The CrUX dataset has several important characteristics:

1. Websites are bucketed by rank magnitude order, not by specific rank.
   Rank will be 1000, 10K, 100K, 1M, etc. in the provided files. The data is
   ordered by rank magnitude. Within each order of magnitude, websites are
   listed randomly.

2. Websites are identified by _origin_ (e.g., https://www.google.com) not
   by domain or FQDN.

3. Data is released monthly, typically on the second Tuesday of the month.

This is an example of what the data looks like:

```
origin,rank
https://www.ptwxz.com,1000
https://ameblo.jp,1000
https://danbooru.donmai.us,1000
https://game8.jp,1000
https://www.google.com.au,1000
https://www.repubblica.it,1000
https://www.w3schools.com,1000
https://animekimi.com,1000
```

Websites are ranked by completed pageloads (measured by First Contentful Paint) and aggregated by web origin. The dataset adheres as closely as possible to user-initiated pageloads (e.g., it excludes traffic from iframes). More information about CrUX and its data collection methodology can be found on its official website: https://developer.chrome.com/docs/crux/about/.

### Data Coverage

This repository contains the complete website ranking data published by Chrome, which includes approximately 15M websites globally. Here's the approximate breakdown of user traffic coverage:

| Websites    | Page Loads  |
| ----------- | ----------- |
| 1000        | 50%         |
| 10K         | 70%         |
| 100K        | 87%         |
| 1M          | 95%         |
| 5M          | 99%         |
| 15M         | 100%        |

### Automated Updates

This repository automatically updates the data monthly using GitHub Actions. The workflow:
1. Authenticates with Google Cloud using repository secrets
2. Queries the latest data from BigQuery
3. Commits and pushes the updated data files

To set up your own instance of this repository:

1. Create a Google Cloud service account with BigQuery access
2. Add the service account JSON credentials as a repository secret named `bq`
3. Enable Git LFS for handling the large data files:
   ```bash
   git lfs install
   git lfs track "data/**/*.csv.gz"
   git add .gitattributes
   ```

### Country-Specific Websites

[Ruth et al.](https://zakird.com/papers/browsing.pdf) showed that browsing behavior is localized and a global top list skews towards global sites (e.g., technology and gaming) and away from local sites (e.g., education, government, and finance). As such, researchers may also want to investigate whether trends hold across individual countries.

<p align="center">
<img width="500" alt="Skew in Websites" src="https://user-images.githubusercontent.com/201296/210107148-3d0f8a03-dbf5-43fc-8ae8-072dbb97fb15.png">
</p>

Chrome publishes country-specific top lists in BigQuery and this repository can also fetch country-specific data.

The CrUX dataset is based on data collected from Google Chrome and is thus biased away from countries with limited Chrome usage (e.g., China). If you're specifically interested in looking at domain popularity in China, consider [Building an Open, Robust, and Stable Voting-Based Domain Top List](https://faculty.cc.gatech.edu/~frankli/papers/xie_usenix2022.pdf), which is based on data collected from 114DNS, a large DNS provider in China.

### Supporting Research

The data in this repo is all publicly posted by Google to their CrUX dataset in Google BigQuery. This is simply a cache of that public data. Many of the arguments in this README are based on two recent research papers:

**[Toppling Top Lists: Evaluating the Accuracy of Popular Website Lists](https://zakird.com/papers/toplists.pdf)**<br/>
Kimberly Ruth, Deepak Kumar, Brandon Wang, Luke Valenta, and Zakir Durumeric<br/>
_ACM Internet Measurement Conference_ (IMC), October 2022

**[A World Wide View of Browsing the World Wide Web](https://zakird.com/papers/browsing.pdf)**<br/>
Kimberly Ruth, Aurore Fass, Jonathan Azose, Mark Pearson, Emma Thomas, Caitlin Sadowski, and Zakir Durumeric<br/>
_ACM Internet Measurement Conference_ (IMC), October 2022

