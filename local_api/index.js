import express from "express"
import cors from "cors"
import {checkLicense, postMultipleFeeds, postSingleFeed} from "./utils.js"

const app = express()
app.use(express.json())
app.use(cors())

const PORT = 80

app.get("/",(req,res)=>{
    res.status(200).send("")

    const timeStamp = new Date.now()
    console.log("API pinged at: ", timeStamp)
    console.log("Payload contained: ", req?.body)
})

app.get("/check_license",checkLicense)

app.post("/multifeed",postMultipleFeeds)
app.post("/singlefeed",postSingleFeed)


app.listen(PORT, ()=>{
    console.log(`Now listening to PORT ${PORT}...`)
    console.log("ip: 73.244.238.97")
})

