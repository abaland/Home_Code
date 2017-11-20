package com.example.abaland.android_remote;

import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import org.w3c.dom.Document;

import java.util.HashMap;


class HeartbeatChecks {

    private MainActivity activity;

    private Button querryButton;
    private LinearLayout querryResults;
    private HashMap<String, TextView> workerViews = new HashMap<>();

    private RabbitCallback callbackObject;


    HeartbeatChecks(MainActivity activity) {

        this.activity = activity;

    }


    /**
     * Applies appropriate function when button on GUI is clicked.
     */
    private void onClickFunction(){

        MainActivity activity = HeartbeatChecks.this.activity;

        String messageToSend = "<instruction type=\"heartbeat\" target=\"bedroom,living\"/>";

        for (TextView view: workerViews.values()) {

            view.setText("");
        }

        activity.rabbitManager.askWorker("heartbeat", messageToSend, activity,
                callbackObject, 5000);



    }


    /**
     */
    private void setUpCallbackFunction() {

        callbackObject = new RabbitCallback() {

            @Override
            public void execute(final Document messageToProcess) {

                // Starts an UI-interactive thread to update the view with the received message.
                activity.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                        String workerId = messageToProcess.getDocumentElement().getAttribute("id");

                        TextView responseView = GeneralFunctions.getWorkerView(activity,
                                workerViews, workerId);

                        responseView.setText(String.format("%s: Active.", workerId));
                        querryResults.addView(responseView);

                    }

                });

            }

        };

    }


    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        querryButton = (Button) this.activity.findViewById(R.id.heartbeat_querry);

        querryResults = (LinearLayout) this.activity.findViewById(R.id.heartbeat_layout);

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
