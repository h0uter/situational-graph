import vedo

vedo.settings.allow_interaction = True


plot_a = vedo.Plotter(interactive=False, shape="2|1")
# plot_a = vedo.Plotter(shape=(1, 5))
# plot_a = vedo.Plotter(interactive=False)
plot_b = vedo.Plotter(interactive=False)
print(plot_a)

step = 0


while True:
    plot_a.at(1).clear()
    plot_a.at(2).clear()
    plot_b.clear()
    # plot_a.clear(at=0)
    # plot_a.clear(at=1)
    # plot_a.clear(at=2)
    plot_a.at(1).show(vedo.Text2D("step: " + str(step)), at=1, rate=1)
    plot_a.at(2).show(vedo.Text2D("my name is jeff: " + str(step)), at=2, rate=1)
    plot_b.show(vedo.Text2D("my name is jeff too: " + str(step)), rate=1)

    step += 1
    print(f"step: {step}")
    # plot_a.show(at=1, rate=1)
    # plot_a.show(at=2, rate=1)
    # plot_a.show(at=1)
    # plot_a.show(at=2)

    if plot_a.escaped:
        break  # if ESC is hit during the loop

plot_a.close()
plot_b.close()
