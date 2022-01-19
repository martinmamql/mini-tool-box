# Save checkpoint for every unique runs using time stamp

# Credit: https://github.com/martinmamql/lcifr

project_root = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
base_dir = path.join(
    f'{args.dataset}',
    # ... hyper-parameter choices
)

models_dir = path.join(project_root, 'save', base_dir)
makedirs(models_dir, exist_ok=True)

# ... training

torch.save(
    model.state_dict(),
    path.join(models_dir, f'model_{epoch}.pt')
)
