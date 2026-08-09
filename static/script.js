document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("issueForm");

    if (!form) {
        console.error("Issue form not found.");
        return;
    }

    let latestAnalysis = null;

    // ==========================
    // AI ANALYSIS
    // ==========================

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        const location =
            document.getElementById("location").value.trim();

        const category =
            document.getElementById("category").value;

        const description =
            document.getElementById("description").value.trim();

        if (!location || !category || !description) {

            alert("Please fill in all required fields.");

            return;
        }

        const analyzeButton =
            form.querySelector('button[type="submit"]');

        analyzeButton.textContent =
            "🤖 Analyzing...";

        analyzeButton.disabled = true;

        try {

            const response = await fetch("/analyze", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    location: location,
                    category: category,
                    description: description

                })

            });


            if (!response.ok) {

                throw new Error(
                    "Server returned " + response.status
                );

            }


            const result =
                await response.json();


            console.log(
                "Analysis result:",
                result
            );


            if (!result.success) {

                throw new Error(
                    result.error || "Analysis failed"
                );

            }


            // Store analysis for submission

            latestAnalysis = result;


            // ==========================
            // DISPLAY AI RESULTS
            // ==========================

            document.getElementById(
                "resultCategory"
            ).textContent =
                result.category || category;


            document.getElementById(
                "resultPriority"
            ).textContent =
                (result.priority || "MEDIUM")
                + " — "
                + (result.score || 0)
                + "/100";


            document.getElementById(
                "resultDepartment"
            ).textContent =
                result.department || "Relevant Civic Department";


            document.getElementById(
                "resultInsight"
            ).textContent =
                result.insight ||
                "AI has analyzed the reported civic issue.";


            document.getElementById(
                "resultAction"
            ).textContent =
                result.action ||
                "Submit the issue to the appropriate department.";


            // ==========================
            // SHOW ANALYSIS SECTION
            // ==========================

            const analysisResult =
                document.getElementById(
                    "analysisResult"
                );


            if (analysisResult) {

                analysisResult.style.display =
                    "block";


                analysisResult.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }


        } catch (error) {

            console.error(
                "Analysis error:",
                error
            );


            alert(
                "Something went wrong while analyzing the issue. Please try again."
            );


        } finally {

            analyzeButton.textContent =
                "🤖 Analyze with CivicSense AI";

            analyzeButton.disabled =
                false;

        }

    });


    // ==========================
    // SUBMIT CIVIC REPORT
    // ==========================

    const submitButton =
        document.getElementById(
            "submitReportBtn"
        );


    if (!submitButton) {

        console.error(
            "Submit Report button not found."
        );

        return;

    }


    submitButton.addEventListener(
        "click",
        async function () {


            // Make sure analysis happened first

            if (!latestAnalysis) {

                alert(
                    "Please analyze the issue first."
                );

                return;

            }


            submitButton.textContent =
                "Submitting...";

            submitButton.disabled =
                true;


            try {


                // ==========================
                // CREATE FORM DATA
                // ==========================

                const formData =
                    new FormData();


                formData.append(
                    "location",
                    document.getElementById(
                        "location"
                    ).value
                );


                formData.append(
                    "category",
                    document.getElementById(
                        "category"
                    ).value
                );


                formData.append(
                    "description",
                    document.getElementById(
                        "description"
                    ).value
                );


                formData.append(
                    "priority",
                    latestAnalysis.priority || "MEDIUM"
                );


                formData.append(
                    "score",
                    latestAnalysis.score || 0
                );


                formData.append(
                    "department",
                    latestAnalysis.department || ""
                );


                formData.append(
                    "insight",
                    latestAnalysis.insight || ""
                );


                formData.append(
                    "action",
                    latestAnalysis.action || ""
                );


                // ==========================
                // ADD PHOTO
                // ==========================

                const photoInput =
                    document.getElementById(
                        "photo"
                    );


                if (
                    photoInput &&
                    photoInput.files &&
                    photoInput.files.length > 0
                ) {

                    formData.append(
                        "photo",
                        photoInput.files[0]
                    );

                }


                // ==========================
                // SEND REPORT
                // ==========================

                const response =
                    await fetch(
                        "/submit-report",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "Server returned " +
                        response.status
                    );

                }


                const result =
                    await response.json();


                console.log(
                    "Submission result:",
                    result
                );


                if (!result.success) {

                    throw new Error(
                        result.error ||
                        "Report submission failed"
                    );

                }


                // ==========================
                // SHOW REPORT ID
                // ==========================

                const reportId =
                    result.report_id ||
                    "CS-" +
                    Math.floor(
                        10000000 +
                        Math.random() *
                        90000000
                    );


                const reportIdElement =
                    document.getElementById(
                        "reportId"
                    );


                if (reportIdElement) {

                    reportIdElement.textContent =
                        reportId;

                }


                const successBox =
                    document.getElementById(
                        "submissionSuccess"
                    );


                if (successBox) {

                    successBox.style.display =
                        "block";

                    successBox.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });

                }


                submitButton.textContent =
                    "✓ Report Submitted";


                submitButton.disabled =
                    true;


            } catch (error) {

                console.error(
                    "Submission error:",
                    error
                );


                alert(
                    "Could not submit the report. Please try again."
                );


                submitButton.textContent =
                    "✅ Submit Civic Report";


                submitButton.disabled =
                    false;

            }

        }
    );

});