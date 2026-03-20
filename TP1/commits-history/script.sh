curl -X POST https://api.github.com/graphql \
  -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user(login: \"nicomoccagatta\") { contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }"}'
