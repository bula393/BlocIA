import { render } from '@testing-library/react';
import { MarkdownContent } from '../../src/components/MarkdownContent';

test('renders inline and display LaTeX as typeset math', () => {
  const content = String.raw`Si $a \ge 0$, la raíz de $a$ cumple:

$$
b^2 = a
$$

**Notación clave:**`;
  const { container, getByText } = render(<MarkdownContent content={content} />);

  expect(getByText('Notación clave:')).toBeInTheDocument();
  expect(container.querySelectorAll('.katex').length).toBe(3);
  expect(container.querySelectorAll('.katex-display').length).toBe(1);
  expect(container.querySelector('.katex-mathml')).toBeInTheDocument();
});
