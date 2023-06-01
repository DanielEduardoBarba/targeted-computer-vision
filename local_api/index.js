import express from "express"
import cors from "cors"
import {checkLicense, postMultipleFeeds, postSingleFeed} from "./utils.js"

const app = express()
app.use(express.json())
app.use(cors())

const PORT = 4040

app.get("/",(req,res)=>{
    res.send("API works...")
    console.log("API pinged...")
})

app.get("/check_license",checkLicense)

app.post("/manyfeeds",postMultipleFeeds)
app.post("/singlefeed",postSingleFeed)


app.listen(PORT, ()=>{
    console.log(`Now listening to PORT ${PORT}...`)
})