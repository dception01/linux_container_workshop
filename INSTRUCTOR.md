# My workshop preparation notes

Before the live session, I’m planning a trial run with four or five students. These are the checks to work through during that session.

- Run all commands inside a clean Ubuntu VM once, including the no-database preview.
- Time four or five students following the labs without narration.
- Verify guest/host browser access on the laptop and a second machine.
- Submit feedback with HTML characters and verify it displays as text.
- Confirm both serving instances appear through port 8081.
- Stop app1 and observe the remaining instance, then recover it.
- Recreate containers without removing volumes; verify feedback survives.
- Stop PostgreSQL and contrast /healthz with /readyz.
- Publish the image, make the package public and test an anonymous pull.
- Load the image archive on another amd64 VM and start without internet.
- Freeze the workshop release after this rehearsal; pre-download student images.

My planned six-hour schedule: introduction 15m; Linux 45m; first container 40m; break 10m; application build 45m; database/network/volume 55m; break 10m; Compose review 30m; load balancing 35m; troubleshooting 40m; presentations and platform connection 35m.

At each checkpoint, I’ll ask teams to explain what happened and why. Team members can rotate between running commands, reading instructions, testing and troubleshooting. If we have only five hours, I’ll demonstrate load balancing and keep the presentations shorter.

The workshop covers local deployment, networking, storage and manual scaling. Authentication, public hosting, TLS, autoscaling and database replication are outside this session.
