import mongoose from 'mongoose';

const connectDB = async () => {
    try {
        // We use process.env to keep your cluster password safe!
        const conn = await mongoose.connect(process.env.MONGO_URI);
        console.log(`📦 MongoDB Connected Successfully: ${conn.connection.host}`);
    } catch (error) {
        console.error('❌ MongoDB Connection Error:', error.message);
        // Exit process with failure if DB doesn't connect
        process.exit(1); 
    }
};

export default connectDB;