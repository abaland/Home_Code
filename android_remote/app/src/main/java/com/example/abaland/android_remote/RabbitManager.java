package com.example.abaland.android_remote;

import com.rabbitmq.client.*;
import android.support.v7.app.AppCompatActivity;

import java.io.IOException;
import java.util.HashMap;
import java.util.concurrent.TimeoutException;
import java.util.UUID;

class RabbitManager {

    private ConnectionFactory factory = new ConnectionFactory();
    private Connection connection;
    private Channel channel;


    RabbitManager() {

        String HostIp = "192.168.3.5";
        String RabbitUser = "adrien";
        String RabbitPassword = "password";

        // Initializes connectionFactory parameters, to start connexions with server
        factory.setHost(HostIp);
        factory.setUsername(RabbitUser);
        factory.setPassword(RabbitPassword);

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

            if (channel == null || connection == null) {

                // Initializes connection and channel with the RabbitMQ server.
                connection = factory.newConnection();
                channel = connection.createChannel();

            }

            // Succeeded : return true.
            /////////////
            return true;
            /////////////

        } catch (IOException | TimeoutException e) {

            // Connection failed. Prints exception, resets parameters, and returns failure status.
            new CustomLogger("Rabbit", "Could not create Rabbit channel : " + e.getMessage(),
                    context, true);

            connection = null;
            channel = null;

            //////////////
            return false;
            //////////////

        }

    }


    /**
     * Checks whether the channel is still open and resets paraeters otherwise
     */
    private void checkChannelParameters() {

        // Resets parameters if the channel is closed.
        if (channel != null && !channel.isOpen()){

            connection = null;
            channel = null;

        }

    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param messageToSend Message to send through RabbitMQ
     * @param context Activity that called the publishMessage function
     */
    private void publishMessage(final String instructionName, final String messageToSend,
                        final AMQP.BasicProperties properties, final AppCompatActivity context) {

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                channel.confirmSelect();
                channel.basicPublish("ex", instructionName, false, properties,
                        messageToSend.getBytes());

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

    }


    /**
     * Declares a temporary queue messages from the server and declares the feed from this queue
     *
     * @param callback Consumer object that contains the callback function to be called
     * @param context Activity that called the publishMessage function
     */
    private String declareTemporaryQueue(final Consumer callback, final AppCompatActivity context) {

        String queueName = null;

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                queueName = channel.queueDeclare().getQueue();
                channel.basicConsume(queueName, false, callback);
                System.out.println("Temporary queue created");

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

        return queueName;

    }


    /**
     * Declares a temporary queue messages from the server and declares the feed from this queue
     *
     * @param queueName Name of queue to be removed
     * @param context Activity that called the publishMessage function
     */
    private void removeTemporaryQueue(final String queueName, final AppCompatActivity context) {

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                channel.queueDelete(queueName);

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

    }


    /**
     * Declares a temporary queue messages from the server and declares the feed from this queue
     *
     * @param deliveryTag ??
     * @param context Activity that called the publishMessage function
     */
    private void acknowledgeMessage(final long deliveryTag, final AppCompatActivity context) {

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                channel.basicAck(deliveryTag, false);

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

    }


    /**
     * Make Java-RabbitMQ-formatted object to handle callback on response from worker after this
     * program send a request.
     *
     * @param callback Object to know how to process response from worker
     * @param context Activity that called the publishMessage function
     * @return RabbitMQ consumer to process response from server
     */
    private Consumer makeConsumer(final RabbitCallback callback, final AppCompatActivity context) {

        return new DefaultConsumer(channel) {

            @Override
            public void handleDelivery(String consumerTag, Envelope envelope,
                                       AMQP.BasicProperties properties,
                                       byte[] messageReceived) throws IOException {

                try {
                    String messageAsString = new String(messageReceived, "UTF-8");
                    callback.execute(messageAsString);

                } catch (RuntimeException e) {

                    System.out.println(" [.] " + e.toString());

                }

                acknowledgeMessage(envelope.getDeliveryTag(), context);

            }

        };
    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param messageToSend Message to send through RabbitMQ
     * @param context Activity that called the publishMessage function
     */
    void askWorker(final String instructionName, final String messageToSend,
                   final AppCompatActivity context) {

        Thread publishThread = new Thread(new Runnable() {

            @Override
            public void run() {

                HashMap<String, Object> messageHeaders = new HashMap<>();
                messageHeaders.put("type", instructionName);
                AMQP.BasicProperties messageProperties = new AMQP.BasicProperties
                        .Builder()
                        .headers(messageHeaders)
                        .build();
                publishMessage(instructionName, messageToSend, messageProperties, context);

            }

        });

        publishThread.start();

    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param messageToSend Message to send through RabbitMQ
     * @param context Activity that called the publishMessage function
     */
    void askWorker(final String instructionName, final String messageToSend,
                   final AppCompatActivity context, final RabbitCallback callbackObject,
                   final int timeoutDuration) {

        Thread publishThread = new Thread(new Runnable() {

            @Override
            public void run() {

                long timeoutStamp = System.currentTimeMillis() + (long) timeoutDuration;

                System.out.println("Timeout stamp computed");
                Consumer callback = makeConsumer(callbackObject, context);
                System.out.println("Consumer created");
                String queueName = declareTemporaryQueue(callback, context);
                System.out.println("Temporary queue declared");

                String corrId = UUID.randomUUID().toString();
                HashMap<String, Object> messageHeaders = new HashMap<>();
                messageHeaders.put("type", instructionName);
                AMQP.BasicProperties messageProperties = new AMQP.BasicProperties
                        .Builder()
                        .correlationId(corrId)
                        .replyTo(queueName)
                        .headers(messageHeaders)
                        .build();
                System.out.println("Properties created");

                publishMessage(instructionName, messageToSend, messageProperties, context);
                System.out.println("Message published");

                // Waits until timeout occurs (see if necessary)
                while(System.currentTimeMillis()<timeoutStamp) {
                    try {
                        Thread.sleep(500);
                    } catch (InterruptedException e) {
                        break;
                    }
                }

                removeTemporaryQueue(queueName, context);
                System.out.println("Queue removed");

            }

        });

        publishThread.start();

    }


}
