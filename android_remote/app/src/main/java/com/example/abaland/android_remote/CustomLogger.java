package com.example.abaland.android_remote;

import android.support.v7.app.AppCompatActivity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.util.Log;

class CustomLogger {


    CustomLogger(String errorTag, String errorMessage, AppCompatActivity context, boolean isSubthread) {

        // Logs message in app log.
        Log.d(errorTag, errorMessage);

        // Creates alert dialog for user to see.
        final AlertDialog.Builder builder1 = new AlertDialog.Builder(context);
        builder1.setMessage(errorMessage);
        builder1.setCancelable(true);
        builder1.setPositiveButton(
                "Ok",
                new DialogInterface.OnClickListener() {

                    public void onClick(DialogInterface dialog, int id) {

                        dialog.cancel();

                    }

                });

        if (!isSubthread) {

            context.runOnUiThread(new Runnable() {
                @Override
                public void run() {

                    AlertDialog alert11 = builder1.create();
                    alert11.show();
                }
            });

        } else {

            AlertDialog alert11 = builder1.create();
            alert11.show();

        }

    }

}
