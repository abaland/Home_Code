package com.example.abaland.android_remote;

import android.view.View;
import android.widget.Button;
import android.widget.TextView;


class TemperatureControls {

    private MainActivity activity;

    private Button querryButton;
    private TextView querryResults;

    private RabbitCallback callbackObject;


    TemperatureControls(MainActivity activity) {

        this.activity = activity;

    }


    /**
     * Applies appropriate function when button on GUI is clicked.
     */
    private void onClickFunction(){

        MainActivity activity = TemperatureControls.this.activity;

        String messageToSend = "<instruction" +
                " type=\"sensors\"" +
                " target=\"bedroom,living\"" +
                "/>";

        activity.rabbitManager.askWorker("sensors", messageToSend, activity,
                callbackObject, 5000);

    }


    /**
     */
    private void setUpCallbackFunction() {

        callbackObject = new RabbitCallback() {

            @Override
            public void execute(final String messageToProcess) {

                // Starts an UI-interactive thread to update the view with the received message.
                activity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        querryResults.setText(messageToProcess);
                    }
                });

            }

        };

    }


    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        querryButton = (Button) this.activity.findViewById(R.id.temperature_querry);

        querryResults = (TextView) this.activity.findViewById(R.id.temperature_results);

    }


    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

        querryButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction();}

        });

    }


    void initialize() {

        setUpCallbackFunction();

        // Links all GUI items to the script
        bindGUIToScript();

        // Adds listeners to GUI, to update internal parameters/take appropriate actions on change
        addGUIListeners();

    }

}
