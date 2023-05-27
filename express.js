import express from "express"
import cors from "cors"

const app = express()
app.use(express.json())
app.use(cors())

const PORT = 4040

app.get("/",(req,res)=>{
    res.send("API works...")
    console.log("API pinged...")
})

app.post("/",(req,res)=>{
    const {sig1} = req.body

    console.log("Sig1: ", sig1)

    res.send({response:"OK!"})
    
    console.log("API POST route pinged...")
})

app.listen(PORT, ()=>{
    console.log(`Now listening to PORT ${PORT}...`)
})