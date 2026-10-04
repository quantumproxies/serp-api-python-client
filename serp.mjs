// SERP API: one POST /v1/serp, parsed search results back.
//
//   export QUANTICDATA_API_KEY=...        # https://app.quanticdata.io/register
//   node serp.mjs "best coffee grinder" us
//
// Node 18+, no dependencies.
// Docs: https://quanticdata.io/docs/#serp

const KEY = process.env.QUANTICDATA_API_KEY;
if (!KEY) {
  console.error("Set QUANTICDATA_API_KEY first: https://app.quanticdata.io/register");
  process.exit(1);
}
const [query = "best coffee grinder", country = "us"] = process.argv.slice(2);

const res = await fetch("https://api.quanticdata.io/v1/serp", {
  method: "POST",
  headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
  body: JSON.stringify({ query, engine: "google", country }),
});
const body = await res.json();
if (!res.ok || body.type === "error") {
  console.error(`Request failed (${res.status}): ${body.message}`);
  process.exit(1);
}
const { payload } = body;

for (const row of payload.organic ?? []) console.log(row.rank, row.title, row.link);
for (const r of payload.related_searches ?? []) console.log("related:", r.query);
