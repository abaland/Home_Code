package com.example.abaland.android_remote;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import android.support.v7.app.AppCompatActivity;

import java.io.IOException;
import java.util.concurrent.TimeoutException;


class Rabbit_Manager {

    private ConnectionFactory factory = new ConnectionFactory();
    private Connection connection;
    private Channel channel;

    private String InstructionName = "remote_control";


    Rabbit_Manager() {

        String HostIp = "192.168.3.7";
        String RabbitUser = "adrien";
        String RabbitPassword = "password";

        // Initializes connectionFactory parameters, to start connexions with server
        factory.setHost(HostIp);
        factory.setUsername(RabbitUser);
        factory.setPassword(RabbitPassword);

    }


    /**
     * Converts the KeyToPressName into a XML-formatted instruction which presses that button
     *
     * @param RemoteName Name of the remote according to rabbitmq
     * @param ConfigToSend Key that must be pressed
     */
    private String convertToXmlInstruction(String RemoteName, String ConfigToSend){

        String RabbitWorkerId = "living-pi";

        String Message_To_Send;

        Message_To_Send = "<instruction" +
                " type=\"" + InstructionName + "\"" +
                " target=\"" + RabbitWorkerId + "\"" +
                " remote=\"" + RemoteName + "\"" +
                " config=\"" + ConfigToSend + "\"" +
                "/>";

        ////////////////////////
        return Message_To_Send;
        ////////////////////////

    }



    /**
     * Attempts to connect to the RabbitMQ server.
     *
     * @param context Activity that called the publishMessage function
     * @return whether creation of channel was successfull or not.
     */
    private boolean createRabbitChannel(AppCompatActivity context) {

        // Attempts to connect to the server (only one attempt)
        try {

            // Initializes connection and channel with the RabbitMQ server.
            connection = factory.newConnection();
            channel = connection.createChannel();

            // Succeeded : return true.
            /////////////
            return true;
            /////////////

        } catch (IOException | TimeoutException e) {


            // Connection failed. Prints exception, resets parameters, and returns failure status.
            new CustomLogger("Rabbit", "Could not create Rabbit channel : " + e.getMessage(), context, true);

            connection = null;
            channel = null;

            //////////////
            return false;
            //////////////

        }

    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param RemoteName Name of the remote according to rabbitmq
     * @param ConfigToSend Key that must be pressed
     * @param context Activity that called the publishMessage function
     */
    void publishMessage(String RemoteName, String ConfigToSend, final AppCompatActivity context) {

        final String MessageToSend = convertToXmlInstruction(RemoteName, ConfigToSend);

        Thread publishThread = new Thread(new Runnable() {

            @Override
            public void run() {

                // Resets parameters if the channel is closed.
                if (channel != null && channel.isOpen()){

                    connection = null;
                    channel = null;

                }

                // Creates connexion with RabbitMQ server if it did not exist already.
                if (createRabbitChannel(context)) {

                    // Sends message.
                    try {

                        channel.confirmSelect();
                        channel.basicPublish("ex", InstructionName, false, null, MessageToSend.getBytes());

                    } catch (IOException e) {

                        // Failed to publish message. Log error and stops
                        new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " + e.getMessage(), context, true);

                    }

                }

            }

        });

        publishThread.start();

    }

}
