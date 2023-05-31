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

const pretend_db={
    registered_motherboard:"/6M9Y362/CN129635AF01A3/",
    registered_cameras:[
        "rtsp://admin:admin@192.168.0.200/11",
        "rtsp://admin:admin@192.168.0.200/11"]
}

app.get("/check_license/",(req,res)=>{
        const mid=req.body.mid
        const cip=req.body.cip

        console.log("Recieved: ", req.body)

        if(mid==pretend_db.registered_motherboard && pretend_db.registered_cameras.includes(cip) ){
            res.status(200).send({license:"valid",response:"OK!"})
        }else{
            res.status(200).send({license:"invalid",response:"OK!"})
        }
       
    
    console.log("API verify route pinged...")
})

app.listen(PORT, ()=>{
    console.log(`Now listening to PORT ${PORT}...`)
})